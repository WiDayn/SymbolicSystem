from pyswip import Prolog

from configs.config import prolog_path

prolog = Prolog()
prolog.consult(prolog_path)
prolog.query("set_prolog_flag(unknown, fail)")
