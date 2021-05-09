import a107

statements = ['energumeno"',
              "Teu cu",
              '"baba" =       "\\\\"         "caca"'
              ]
for statement in statements:
    try:
        args, kwargs = a107.str2args(statement)
        print(statement, "--->", args, kwargs)
        pass
    except a107.StatementError as e:
        print(e.explain())
