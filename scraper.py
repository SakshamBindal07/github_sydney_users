import requests
import csv
import time

GITHUB_TOKEN = 'YOUR_GITHUB_TOKEN'
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}
BASE_URL = 'https://api.github.com'
USER_QUERY = 'location:Sydney followers:>100'
MAX_REPOS = 500 

def fetch_users():
    users = []
    url = f"{BASE_URL}/search/users?q={USER_QUERY}&per_page=100"
    while url:
        response = requests.get(url, headers=HEADERS)
        data = response.json()
        
        if 'items' in data:
            for user in data['items']:
                user_data = requests.get(user['url'], headers=HEADERS).json()
                if user_data:
                    users.append(process_user_data(user_data))
        
        if 'next' in response.links:
            url = response.links['next']['url']
        else:
            url = None
        
        time.sleep(1)
    return users

def process_user_data(user):
    company = user.get('company', '').strip().lstrip('@').upper() if user.get('company') else ''
    return {
        'login': user.get('login', ''),
        'name': user.get('name', ''),
        'company': company,
        'location': user.get('location', ''),
        'email': user.get('email', ''),
        'hireable': str(user.get('hireable', '')),
        'bio': user.get('bio', ''),
        'public_repos': user.get('public_repos', ''),
        'followers': user.get('followers', ''),
        'following': user.get('following', ''),
        'created_at': user.get('created_at', '')
    }

def fetch_repositories(login):
    repos = []
    page = 1
    while len(repos) < MAX_REPOS:
        url = f"{BASE_URL}/users/{login}/repos?per_page=100&sort=pushed&page={page}"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code != 200:
            print(f"Error fetching repositories for {login}: {response.status_code}")
            break

        data = response.json()
        
        if not data:
            break

        for repo in data:
            repos.append(process_repo_data(repo, login))
        
        page += 1
        time.sleep(1)

    return repos[:MAX_REPOS]

def process_repo_data(repo, login):
    license_name = repo['license']['key'] if repo.get('license') else ''
    return {
        'login': login,
        'full_name': repo.get('full_name', ''),
        'created_at': repo.get('created_at', ''),
        'stargazers_count': repo.get('stargazers_count', 0),
        'watchers_count': repo.get('watchers_count', 0),
        'language': repo.get('language', ''),
        'has_projects': str(repo.get('has_projects', '')),
        'has_wiki': str(repo.get('has_wiki', '')),
        'license_name': license_name
    }

def write_csv(filename, fieldnames, rows):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main():
    users = fetch_users()
    user_repos = []
    for user in users:
        user_repos.extend(fetch_repositories(user['login']))
    
    user_fields = ['login', 'name', 'company', 'location', 'email', 'hireable', 'bio', 'public_repos', 'followers', 'following', 'created_at']
    write_csv('users.csv', user_fields, users)

    repo_fields = ['login', 'full_name', 'created_at', 'stargazers_count', 'watchers_count', 'language', 'has_projects', 'has_wiki', 'license_name']
    write_csv('repositories.csv', repo_fields, user_repos)

if __name__ == '__main__':
    main()
