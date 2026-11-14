from search import search_prompt

EXIT_COMMANDS = {"sair", "exit", "quit"}


def main():
    try:
        chain = search_prompt()
    except Exception as e:
        print(f"Não foi possível iniciar o chat: {e}")
        return

    print("Chat iniciado. Digite 'sair' para encerrar.")

    while True:
        try:
            pergunta = input("\nFaça sua pergunta: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not pergunta:
            print("Por favor, faça uma pergunta.")
            continue

        if pergunta.lower() in EXIT_COMMANDS:
            break

        try:
            resposta = chain.invoke(pergunta)
        except KeyboardInterrupt:
            print()
            break
        except Exception as e:
            print(f"Erro ao processar a pergunta: {e}")
            continue

        print(f"\nPERGUNTA: {pergunta}")
        print(f"RESPOSTA: {resposta}")

    print("Até logo!")


if __name__ == "__main__":
    main()
