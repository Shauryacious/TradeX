# SSL Certificate Troubleshooting

Guide to fix SSL certificate verification errors on macOS.

## Problem

You may see errors like:
```
SSLCertVerificationError: certificate verify failed: unable to get local issuer certificate
```

This is a common issue on macOS when Python's SSL certificates aren't properly configured.

## Solution 1: Install Certificates (Recommended)

### Method A: Use Python's Certificate Installer

1. **Find the installer:**
   ```bash
   find /Applications -name "Install Certificates.command"
   ```

2. **Run it:**
   ```bash
   /Applications/Python\ 3.12/Install\ Certificates.command
   ```

### Method B: Manual Certificate Installation

```bash
# Install certifi
pip3 install --upgrade certifi

# Copy certificates to Python's SSL directory
python3 -c "
import certifi
import shutil
import os

cert_dir = '/Library/Frameworks/Python.framework/Versions/3.12/etc/openssl'
os.makedirs(cert_dir, exist_ok=True)
shutil.copy(certifi.where(), f'{cert_dir}/cert.pem')
print('✅ Certificates installed')
"
```

## Solution 2: Set Environment Variables

Add to your `~/.zshrc` or `~/.bash_profile`:

```bash
export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")
export REQUESTS_CA_BUNDLE="$SSL_CERT_FILE"
```

Then reload:
```bash
source ~/.zshrc  # or source ~/.bash_profile
```

## Solution 3: Use the Fix Script

Run the provided script:

```bash
cd server
./scripts/fix_ssl.sh
```

## Solution 4: Development Workaround (Not for Production)

If the above don't work, you can temporarily disable SSL verification for development:

**⚠️ WARNING: Only for development! Never use in production!**

The code already sets SSL environment variables. If issues persist, you may need to:

1. Restart your terminal
2. Restart the server
3. Check that certifi is installed: `pip3 list | grep certifi`

## Verification

Test SSL connection:

```bash
python3 -c "
import ssl
import certifi
ctx = ssl.create_default_context(cafile=certifi.where())
print('✅ SSL context works')
"
```

## Still Having Issues?

1. **Check Python installation:**
   ```bash
   which python3
   python3 --version
   ```

2. **Reinstall certifi:**
   ```bash
   pip3 uninstall certifi
   pip3 install certifi
   ```

3. **Check certificate file:**
   ```bash
   python3 -c "import certifi; print(certifi.where())"
   ls -la $(python3 -c "import certifi; print(certifi.where())")
   ```

4. **Try different Python installation:**
   - If using Homebrew Python: `brew install python@3.12`
   - If using official Python: Reinstall from python.org

## For Production

In production, ensure:
- SSL verification is enabled
- Certificates are properly installed
- Use proper certificate management
- Never disable SSL verification

