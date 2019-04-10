import git
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from distutils.dir_util import copy_tree
import shutil

repo = git.Repo(os.getcwd())
index = git.Repo.init(os.getcwd()).index
# g = git.cmd.Git(os.getcwd())
# g.pull()
#o = repo.remotes.origin
repo.git.pull(os.getcwd())
repo.git.add(u=True)
index.commit("second try")
#repo.git.commit()
#repo.git.push('origin', 'hello')

# repo_date = datetime.now() - relativedelta(days = 7)
# repo_date = repo_date.strftime("-%d-%m-%Y")
#
# fromDirectory =  os.getcwd()
# toDirectory = os.getcwd() + repo_date + '/'
# os.mkdir(toDirectory)
# copy_tree(fromDirectory, toDirectory)
#
# shutil.rmtree(os.getcwd() + repo_date + '/.git')
