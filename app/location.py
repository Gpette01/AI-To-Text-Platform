from ipregistry import IpregistryClient

client = IpregistryClient("tryout")  
ipInfo = client.lookup_ip() 
print(ipInfo)