from graph import add_user_node, add_participates_edge, add_repo_node_with_languages, \
    add_programs_edge, EDGE_IMPLEMENTS, EDGE_PARTICIPATES, NODE_USER

NO_DATE = 'no_date'


def add_users(g, repo, user_commit, main_user):
    for user in user_commit.keys():
        if main_user.login == user.login:
            continue

        add_user_node(g, user)
        add_participates_edge(g, user, repo)


def add_user_repos_with_commits_and_languages(g, user_commit,
                                              max_commit):
    user_repo = user_repo_dictionary(user_commit.keys())
    for user in user_repo.keys():
        for repo in user_repo[user]:
            add_repo_node_with_languages(g, repo)
            add_participates_edge(g, user, repo)

            user_commit = user_commit_dictionary(repo, max_commit)
            add_users(g, repo, user_commit, user)


def user_commit_dictionary(repo, max_commit):
    user_commits = {}
    counter = 0

    for commit in repo.get_commits():
        if counter == max_commit:
            break

        if hasattr(commit.author, 'login') and isinstance(commit.author.login, str):
            if commit.author not in user_commits:
                user_commits[commit.author] = []

            user_commits[commit.author].append(commit.commit)
            counter = counter + 1

    return user_commits


def get_repos_for_user(user):
    repos = []

    for repo in user.get_repos():
        repos.append(repo)

    return repos


def user_repo_dictionary(users):
    user_repos = {}

    for user in users:
        user_repos[user] = get_repos_for_user(user)

    return user_repos


def add_user_language_edges(g):
    users = [n[0] for n in g.nodes(data=True) if n[1]['kind'] == NODE_USER]
    for user in users:
        repos = [n[1] for n in g.edges(data=True) if n[2]['kind'] == EDGE_PARTICIPATES and n[0] == user]
        for repo in repos:
            languages = [n[0] for n in g.edges(data=True) if n[2]['kind'] == EDGE_IMPLEMENTS and n[1] == repo]
            for language in languages:
                add_programs_edge(g, user, language)
