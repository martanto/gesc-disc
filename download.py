import requests
import re
import os.path
import argparse

class SessionWithHeaderRedirection(requests.Session):
    AUTH_HOST = 'urs.earthdata.nasa.gov'
    
    # Constructor
    def __init__(self, username, password):
        super().__init__()
        self.auth = (username, password)

    def rebuild_auth(self, prepared_request, response):
        headers = prepared_request.headers
        url = prepared_request.url

        if 'Authorization' in headers:
            original_parsed = requests.utils.urlparse(response.request.url)
            redirect_parsed = requests.utils.urlparse(url)
            if (original_parsed.hostname != redirect_parsed.hostname) and redirect_parsed.hostname != self.AUTH_HOST and original_parsed.hostname != self.AUTH_HOST:
                del headers['Authorization']
            return

def main():
    parser = argparse.ArgumentParser(description='GESC Downloader')
    parser.add_argument('-username', help='Masukkan username yang terdaftar')
    parser.add_argument('-password', help='Masukkan password')
    args = parser.parse_args()
    session = SessionWithHeaderRedirection(args.username, args.password)

    with open('datalist.dat','r') as urls:
        for url in urls:
            # filename = url[url.rfind('/')+1:]
            # print(filename)
            try:
                response = session.get(url, stream=True)
                print(response.status_code)
                if response.status_code == 200:
                    if response.headers.get('Content-Disposition'):
                        d = response.headers['Content-Disposition']
                        fname = re.findall("filename=(.+)", d)
                        print(fname[0])
                    with open(os.getcwd()+'/downloaded/'+fname[0].strip('\"'), 'wb') as infile:
                        for chunk in response.iter_content(chunk_size=1024*1024):
                            infile.write(chunk)

            except requests.exceptions.HTTPError as e:
                print(e)

if __name__ == '__main__':
    main()