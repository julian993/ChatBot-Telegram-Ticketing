import requests
import json

headers = {
    'X-API-Key': 'xxxxxxxxx',
}
data = {
"name": "Albert",
"email": "testo@gmail.com",
"subject": "",
"message": "",
"topicId": "1",
}
URL = 'http://localhost/OS/api/http.php/tickets/ticketInfo?ticketNumber=598521'
PARAMS = headers
response = requests.get(url = URL, headers = PARAMS)
print(response.content)
#content = response.content.decode("utf8")
#data1 = response.json()

#inserisci luogo meglio specificare
#add comments
#dopo registrazione e poi le faremo sapere
#campo dettagli

https://github.com/osTicket/osTicket/pull/4361/files
