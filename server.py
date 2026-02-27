from openreward.environments import Server

from admepred import AdmePred

if __name__ == "__main__":
    server = Server([AdmePred])
    server.run()
