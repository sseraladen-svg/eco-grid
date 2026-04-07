# Google OAuth Setup Guide

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API and Google OAuth2 API

## Step 2: Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Choose **External** for user type
3. Fill in required information:
   - App name: EcoGrid AI
   - User support email: your-email@example.com
   - Developer contact: your-email@example.com
4. Add required scopes:
   - `.../auth/userinfo.email`
   - `.../auth/userinfo.profile`
   - `openid`

## Step 3: Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
3. Select **Web application**
4. Add authorized redirect URIs:
   - `http://127.0.0.1:5000/auth/google/callback`
   - `http://localhost:5000/auth/google/callback`
5. Click **Create**
6. Copy the **Client ID** and **Client Secret**

## Step 4: Set Environment Variables

Set the following environment variables:

**Windows (Command Prompt):**
```cmd
set GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
set GOOGLE_CLIENT_SECRET=your-google-client-secret
```

**Windows (PowerShell):**
```powershell
$env:GOOGLE_CLIENT_ID="your-google-client-id.apps.googleusercontent.com"
$env:GOOGLE_CLIENT_SECRET="your-google-client-secret"
```

**Linux/Mac:**
```bash
export GOOGLE_CLIENT_ID="your-google-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-google-client-secret"
```

## Step 5: Update Code (Optional)

If you want to hardcode the credentials for development, update `backend/google_auth.py`:

```python
GOOGLE_CLIENT_ID = 'your-google-client-id.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'your-google-client-secret'
```

## Step 6: Test the Integration

1. Restart the Flask server
2. Go to http://127.0.0.1:5000
3. Click the "Google" login button
4. Authorize the application
5. You should be redirected back to the setup page

## Security Notes

- **Never commit credentials to version control**
- Use environment variables in production
- Restrict the OAuth client to your domains only
- Enable app verification for production use

## Troubleshooting

### "redirect_uri_mismatch" Error
- Make sure the redirect URI in Google Console matches exactly
- Check for trailing slashes or http vs https

### "invalid_client" Error
- Verify the Client ID is correct
- Check if the OAuth client is enabled

### "access_denied" Error
- User denied access to the application
- Try again and grant the required permissions

### "invalid_scope" Error
- Make sure all required scopes are added to the OAuth consent screen
- Check scope formatting in the code
