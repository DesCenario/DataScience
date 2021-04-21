import os
from pathlib import Path

import networkx as nx

NODE_REPO = 'repo'
NODE_LANG = 'lang'
NODE_USER = 'user'
EDGE_PARTICIPATES = 'participates'
EDGE_IMPLEMENTS = 'implements'
EDGE_PROGRAMS = 'programs'


def is_graph_saved(name):
    return os.path.isfile(backup_file(name))


def load_graph(name):
    return nx.read_gpickle(backup_file(name))


def save_graph(g, name):
    Path("data").mkdir(parents=True, exist_ok=True)
    nx.write_gpickle(g, backup_file(name))


def backup_file(name):
    return 'data/' + name + '.gpickle'


def is_visual_graph_saved(name):
    return os.path.isfile(gexf_file(name))


def export_visual_graph(g, name):
    nx.write_gexf(g, gexf_file(name))


def gexf_file(name):
    return 'data/' + name + '.gexfG


def new_graph():
    return nx.DiGraph()


def add_repo_node_with_languages(g, repo):
    repo_node_type = NODE_REPO
    repo_node_name = typed_name(repo.full_name, repo_node_type)
    g.add_node(repo_node_name,
               kind=repo_node_type,
               open_issues_count=repo.open_issues_count,
               stargazers_count=repo.stargazers_count,
               forks_count=repo.forks_count)

    language_node_type = NODE_LANG
    for language in repo.get_languages():
        lang_node_name = typed_name(language, language_node_type)
        g.add_node(lang_node_name, kind=language_node_type)
        g.add_edge(lang_node_name, repo_node_name, kind=EDGE_IMPLEMENTS)


def add_user_node(g, user):
    node_type = NODE_USER
    g.add_node(typed_name(user.login, node_type), kind=node_type)


def add_participates_edge(g, user, repo):
    edge_type = EDGE_PARTICIPATES
    g.add_edge(typed_name(user.login, NODE_USER), typed_name(repo.full_name, NODE_REPO), kind=edge_type)


def add_programs_edge(g, typed_user, typed_language):
    edge_type = EDGE_PROGRAMS
    g.add_edge(typed_user, typed_language, kind=edge_type)


def typed_name(name, type):
    return name + '(' + type + ')'
