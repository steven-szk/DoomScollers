
def reset_file():
    open("log.txt", "w").close()


def write_file(status):
    with open("log.txt", "a") as f:
        f.write(f"{status}\n")
