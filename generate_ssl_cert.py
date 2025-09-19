#!/usr/bin/env python3
"""
BackendBot SSL Certificate Generator
====================================

Genera certificados SSL auto-firmados para desarrollo local seguro.
Estos certificados permiten HTTPS en localhost sin acceso externo.

Uso:
    python generate_ssl_cert.py

Esto creará:
- backendbot_cert.pem (certificado)
- backendbot_key.pem (clave privada)

Autor: BackendBot Team
Versión: 0.1.0
"""

import os
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pathlib import Path


def generate_ssl_certificate():
    """Generar certificado SSL auto-firmado para localhost."""

    # Crear directorio de certificados
    cert_dir = Path(__file__).parent / "certs"
    cert_dir.mkdir(exist_ok=True)

    cert_path = cert_dir / "backendbot_cert.pem"
    key_path = cert_dir / "backendbot_key.pem"

    # Verificar si ya existen
    if cert_path.exists() and key_path.exists():
        print("✅ Los certificados SSL ya existen")
        print(f"   Certificado: {cert_path}")
        print(f"   Clave: {key_path}")
        return

    print("🔐 Generando certificado SSL auto-firmado...")

    # Generar clave privada
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Crear certificado
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Madrid"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Madrid"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "BackendBot"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.now(datetime.UTC)
    ).not_valid_after(
        datetime.now(datetime.UTC) + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.DNSName("127.0.0.1"),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())

    # Guardar certificado
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    # Guardar clave privada
    with open(key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    print("✅ Certificado SSL generado correctamente")
    print(f"   Certificado: {cert_path}")
    print(f"   Clave: {key_path}")
    print()
    print("📋 Instrucciones:")
    print("   1. Los certificados son válidos por 1 año")
    print("   2. Solo funcionan en localhost (127.0.0.1)")
    print("   3. Acepta la advertencia de certificado en tu navegador")
    print("   4. Para producción, usa certificados de una CA confiable")


if __name__ == "__main__":
    generate_ssl_certificate()