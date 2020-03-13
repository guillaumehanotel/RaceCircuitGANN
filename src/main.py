from src.app import App



def main():
    app = App()
    app.run(creative_mode=False)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
