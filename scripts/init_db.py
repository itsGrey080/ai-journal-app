import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from app.database import Base, engine

def main():
    Base.metadata.create_all(bind=engine)
    print("Database initialized.")

if __name__ == "__main__":
    main()
