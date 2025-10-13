
# Créer un certificat auto-signé
$cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=Pong Force Studios" -KeyUsage DigitalSignature -FriendlyName "Pong Force Code Signing" -CertStoreLocation "Cert:\CurrentUser\My" -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")

# Exporter le certificat
$certPath = "pong_force_cert.pfx"
$password = ConvertTo-SecureString -String "PongForce2024!" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath $certPath -Password $password

Write-Host "Certificate created: $certPath"
Write-Host "Password: PongForce2024!"
