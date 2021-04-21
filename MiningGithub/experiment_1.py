from github import Github

from graph import new_graph, load_graph, save_graph, is_graph_saved, export_visual_graph, add_repo_node_with_languages, \
    is_visual_graph_saved
from repo import user_commit_dictionary, add_users, add_user_repos_with_commits_and_languages, \
    add_user_language_edges
from stats import get_counted_user_repo_map, \
    get_programming_languages, get_counted_languages_map, get_repos, get_counted_user_language_map, \
    get_counted_repo_issues_map, get_counted_repo_stargazers_map, get_counted_repo_fork_map, get_users, \
    get_counted_repo_users_map

GRAPH_NAME = 'experiment_1'


def new_experiment_1(token, user, repo, max_commit):
    g = new_graph_experiment_1(token=token,
                               user=user,
                               repo=repo,
                               max_commit=max_commit)
    print_stats_experiment_1(g)


def new_graph_experiment_1(token, user, repo, max_commit):
    if is_graph_saved(GRAPH_NAME):
        g = load_graph(GRAPH_NAME)
    else:
        client = Github(token)
        user = client.get_user(user)
        repo = user.get_repo(repo)

        g = new_graph()
        add_repo_node_with_languages(g, repo)
        user_commit = user_commit_dictionary(repo, max_commit=max_commit)
        add_users(g, repo, user_commit, user)
        add_user_repos_with_commits_and_languages(g, user_commit, max_commit=max_commit)
        add_user_language_edges(g)
        save_graph(g, GRAPH_NAME)

    if not is_visual_graph_saved(GRAPH_NAME):
        export_visual_graph(g, GRAPH_NAME)

    return g


def print_stats_experiment_1(g):
    print('Beantwortung der Fragestellungen aus dem Experiment')
    print('===================================================')
    print()

    print_repository_stats(g)
    print_users_stats(g)
    print_language_stats(g)


def print_repository_stats(g):
    print('a) Fragen zum Repository')
    print('------------------------')
    print('i) Wie viele Repositories gibt es im Graphen? \n' +
          'Antwort:' + str(len(get_repos(g))))
    print()

    counted_repo_users_map = get_counted_repo_users_map(g)
    print('ii) Welches Repository hat am meisten Benutzer? \n' +
          'Antwort: ' +
          list(counted_repo_users_map.keys())[0] + ', ' +
          str(list(counted_repo_users_map.values())[0]))
    print()

    counted_open_issues_map = get_counted_repo_issues_map(g)
    print('iii) Welches Repository hat am meisten offene Issues? \n' +
          'Antwort: ' +
          list(counted_open_issues_map.keys())[0] + ', ' +
          str(list(counted_open_issues_map.values())[0]))
    print()

    counted_stargazers_map = get_counted_repo_stargazers_map(g)
    print('iv) Welches Repository ist am populärsten, hat am meisten Stargazers? \n' +
          'Antwort: ' +
          list(counted_stargazers_map.keys())[0] + ', ' +
          str(list(counted_stargazers_map.values())[0]))
    print()

    counted_fork_map = get_counted_repo_fork_map(g)
    print('v) Welches Repository hat am meisten Forks? \n' +
          'Antwort: ' +
          list(counted_fork_map.keys())[0] + ', ' +
          str(list(counted_fork_map.values())[0]))

    print()


def print_users_stats(g):
    print('b) Fragen zu den Benutzern')
    print('--------------------------')
    print('i) Wie viele Benutzer gibt es im Netzwerk?\n'
          + 'Antwort: ' + str(len(get_users(g))))
    print()

    counted_user_repo_map = get_counted_user_repo_map(g)
    print('ii) Welcher Benutzer ist an den meisten Projekten im Graphen beteiligt und an wie vielen?\n' +
          'Antwort: ' +
          list(counted_user_repo_map.keys())[0] + ', ' +
          str(list(counted_user_repo_map.values())[0]))
    print()

    counted_user_language_map = get_counted_user_language_map(g)
    print('iii) Welcher Benutzer verwendet die meisten unterschiedlichen Programmiersprachen?\n' +
          'Antwort: ' +
          list(counted_user_language_map.keys())[0] + ', ' +
          str(list(counted_user_language_map.values())[0]))

    print()


def print_language_stats(g):
    print('c) Fragen zu den Programmiersprachen')
    print('------------------------------------')

    languages = get_programming_languages(g)
    print('i) Wie viele Programmiersprachen gibt es im Netzwerk?\n'
          'Antwort: ' + str(len(languages)))
    counted_languages_map = get_counted_languages_map(g)
    print()

    print('ii) Welche 10 Programmiersprachen wurdem am meisten eingesetzt?\n'
          + 'Antwort: ')
    count = 0
    for language in counted_languages_map.keys():
        if count >= 10:
            break

        print(language + ', ' + str(counted_languages_map[language]))
        count = count + 1
    print()
