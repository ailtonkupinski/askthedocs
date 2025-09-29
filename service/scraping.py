"""
Serviço de Web Scraping

Este módulo implementa o serviço de scraping que utiliza a API do Firecrawl
para extrair conteúdo de websites e criar coleções de documentação.
Suporta crawling assíncrono com polling de status.
"""

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

class ScrapingService:
    """
    Serviço de web scraping usando Firecrawl API.
    
    Funcionalidades:
    - Crawling de websites completos
    - Extração de conteúdo em markdown
    - Salvamento em coleções organizadas
    - Suporte a crawling assíncrono
    """
    
    def __init__(self):
        # Configuração da API Firecrawl
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        self.api_url = os.getenv("FIRECRAWL_API_URL") or "https://api.firecrawl.dev"

    def scrape_website(self, url, collection_name):
        """
        Executa o scraping de um website e salva o conteúdo em uma coleção.
        
        Args:
            url (str): URL do website a ser processado
            collection_name (str): Nome da coleção onde salvar o conteúdo
            
        Returns:
            dict: Resultado do scraping com status e número de arquivos salvos
        """
        try:
            # Inicia o crawling via API Firecrawl
            endpoint = f"{self.api_url.rstrip('/')}/v1/crawl"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {"url": url}
            resp = requests.post(endpoint, json=payload, headers=headers, timeout=120)
            resp.raise_for_status()
            body = resp.json() if resp.content else {}

            # Logs de debug para monitoramento
            try:
                print(f"Response status: {resp.status_code}")
                if isinstance(body, dict):
                    print(f"Response body keys: {list(body.keys())}")
                else:
                    print("Response body is not a dict")
            except Exception:
                pass

            # Verifica se os dados já estão disponíveis ou se precisa fazer polling
            scraped_data = body.get("data", []) if isinstance(body, dict) else []
            job_id = body.get("id") if isinstance(body, dict) else None
            
            # Se não há dados imediatos, faz polling do job assíncrono
            if not scraped_data and job_id:
                status_endpoint = f"{self.api_url.rstrip('/')}/v1/crawl/{job_id}"
                results_endpoint = f"{status_endpoint}/results"

                max_attempts = 30
                for attempt in range(1, max_attempts + 1):
                    time.sleep(2)
                    try:
                        status_resp = requests.get(status_endpoint, headers=headers, timeout=30)
                        status_resp.raise_for_status()
                        status_body = status_resp.json() if status_resp.content else {}
                        try:
                            print(f"Polling {attempt}/{max_attempts} - keys: {list(status_body.keys()) if isinstance(status_body, dict) else 'NA'}")
                        except Exception:
                            pass

                        if isinstance(status_body, dict):
                            status = status_body.get("status") or status_body.get("state")
                            data_in_status = status_body.get("data")
                            if isinstance(data_in_status, list) and data_in_status:
                                scraped_data = data_in_status
                                break
                            if status in ("completed", "success", "finished"):
                                try:
                                    res_resp = requests.get(results_endpoint, headers=headers, timeout=60)
                                    res_resp.raise_for_status()
                                    res_body = res_resp.json() if res_resp.content else {}
                                    if isinstance(res_body, dict) and isinstance(res_body.get("data"), list):
                                        scraped_data = res_body["data"]
                                        break
                                except Exception:
                                    pass
                            if status in ("failed", "error"):
                                raise Exception(status_body.get("error") or "Crawl falhou")
                    except requests.HTTPError as http_err:
                        if http_err.response is not None and http_err.response.status_code == 404:
                            try:
                                res_resp = requests.get(results_endpoint, headers=headers, timeout=60)
                                res_resp.raise_for_status()
                                res_body = res_resp.json() if res_resp.content else {}
                                if isinstance(res_body, dict) and isinstance(res_body.get("data"), list):
                                    scraped_data = res_body["data"]
                                    break
                            except Exception:
                                pass
                        else:
                            raise
            try:
                print(f"Scraped data length: {len(scraped_data) if isinstance(scraped_data, list) else 'N/A'}")
                if isinstance(scraped_data, list) and scraped_data:
                    first_page = scraped_data[0]
                    if isinstance(first_page, dict):
                        print(f"First page keys: {list(first_page.keys())}")
            except Exception:
                pass

            collection_path = f"data/collections/{collection_name}"
            os.makedirs(collection_path, exist_ok=True)

            saved_count = 0
            for i, page in enumerate(scraped_data, 1):
                markdown_content = None
                if isinstance(page, dict):
                    # Tenta diferentes caminhos para o conteúdo
                    if page.get("markdown"):
                        markdown_content = page["markdown"]
                    elif page.get("content"):
                        markdown_content = page["content"]
                    elif isinstance(page.get("data"), dict):
                        if page["data"].get("markdown"):
                            markdown_content = page["data"]["markdown"]
                        elif page["data"].get("content"):
                            markdown_content = page["data"]["content"]
                if not markdown_content:
                    try:
                        keys_info = list(page.keys()) if isinstance(page, dict) else type(page)
                        print(f"Página {i} sem conteúdo markdown: {keys_info}")
                    except Exception:
                        pass
                    continue

                with open(f"{collection_path}/{i}.md", "w", encoding="utf-8") as f:
                    f.write(markdown_content)
                saved_count += 1

            return {"success": True, "files": saved_count}
        
        except Exception as e:
            print(f"Erro ao processar a URL {url}: {str(e)}")
            return {"success": False, "error": str(e)}