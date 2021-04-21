from graph import NODE_REPO, NODE_USER, EDGE_PARTICIPATES, NODE_LANG, EDGE_IMPLEMENTS, EDGE_PROGRAMS


def get_repos(g):
    return filtered_nodes(g, NODE_REPO)


def get_users(g):
    return filtered_nodes(g, NODE_USER)


def get_develops_edges(g):
    return filtered_edges(g, EDGE_PARTICIPATES)


def get_counted_user_repo_map(g):
    user_repo_map = {}

    for edge in get_develops_edges(g):
        user = edge[0]

        if user not in user_repo_map:
            user_repo_map[user] = 0

        user_repo_map[user] = user_repo_map[user] + 1

    return sort_map_desc(user_repo_map)


def get_counted_languages_map(g):
    language_map = {}

    for edge in filtered_edges(g, EDGE_IMPLEMENTS):
        language = edge[0]

        if language not in language_map:
            language_map[language] = 0

        language_map[language] = language_map[language] + 1

    return sort_map_desc(language_map)


def get_counted_user_language_map(g):
    user_language_map = {}

    for edge in filtered_edges(g, EDGE_PROGRAMS):
        user = edge[0]

        if user not in user_language_map:
            user_language_map[user] = 0

        user_language_map[user] = user_language_map[user] + 1

    return sort_map_desc(user_language_map)


def get_counted_repo_users_map(g):
    repo_user_map = {}

    for edge in filtered_edges(g, EDGE_PARTICIPATES):
        repo = edge[1]

        if repo not in repo_user_map:
            repo_user_map[repo] = 0

        repo_user_map[repo] = repo_user_map[repo] + 1

    return sort_map_desc(repo_user_map)


def get_counted_repo_issues_map(g):
    return get_counted_repo_map(g, 'open_issues_count')


def get_counted_repo_stargazers_map(g):
    return get_counted_repo_map(g, 'stargazers_count')


def get_counted_repo_fork_map(g):
    return get_counted_repo_map(g, 'forks_count')


def get_counted_repo_map(g, attribute):
    repo_issues_map = {}

    for node in filtered_nodes(g, NODE_REPO):
        repo = node[0]
        repo_issues_map[repo] = node[1][attribute]

    return sort_map_desc(repo_issues_map)


def sort_map_desc(to_be_sorted):
    sorted_map = {}
    for element in sorted(to_be_sorted, key=to_be_sorted.get, reverse=True):
        sorted_map[element] = to_be_sorted[element]
    return sorted_map


def get_programming_languages(g):
    return filtered_nodes(g, NODE_LANG)


def filtered_nodes(g, node_type):
    return [n for n in list(g.nodes(data=True)) if n[1]['kind'] == node_type]


def filtered_edges(g, edge_type):
    return [e for e in list(g.edges(data=True)) if e[2]['kind'] == edge_type]
