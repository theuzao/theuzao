"""Gera o GIF de terminal do topo do README.

Usa https://github.com/x0rzavi/github-readme-terminal (pacote `gifos`).
Roda pelo workflow .github/workflows/update-readme.yml, mas pode ser
executado localmente com um simples `python main.py` - o conteudo e todo
estatico, entao nao precisa de GITHUB_TOKEN.

Diferente do exemplo upstream, este script NAO reescreve o README inteiro:
ele troca apenas o bloco entre os marcadores START/END_SECTION:terminal.
"""

import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import gifos

USERNAME = "theuzao"
FULL_NAME = "Matheus Guilherme"
EMAIL = "matheussanti.contato@gmail.com"
WEBSITE = "theuzao.dev"
LINKEDIN = "theuzao"
LOCATION = "Belo Horizonte, Brazil"
SCHOOL = "PUC Minas - Software Engineering"

TIMEZONE = ZoneInfo("America/Sao_Paulo")

RULE = "-"

README = Path(__file__).with_name("README.md")
START = "<!--START_SECTION:terminal-->"
END = "<!--END_SECTION:terminal-->"

C_KEY, C_VAL, C_OK, C_HDR = "\x1b[96m", "\x1b[93m", "\x1b[92m", "\x1b[30;102m"
R = "\x1b[0m"

PROMPT = f"\x1b[0;91m{USERNAME}\x1b[0m@\x1b[0;93mjvm-os ~> \x1b[0m"

TYPING = 1
BEAT = 2
HOLD_FINAL = 55

ROW_H = 18
YPAD = 15
CONTENT_ROWS = 25


def boot_sequence(t: gifos.Terminal, year: str) -> None:
    """Tela de BIOS com sabor de JVM - o 'boot' do perfil."""
    t.toggle_show_cursor(False)
    t.gen_text(f"{FULL_NAME} - Modular BIOS v21.0.2", 1)
    t.gen_text(f"Copyright (C) {year}, \x1b[31m{FULL_NAME}{R}", 2)
    t.gen_text(f"\x1b[94mGitHub Profile Terminal, Rev 2026{R}", 4)
    t.gen_text("JVM HotSpot(tm) 64-Bit Server VM - 21.0.2 LTS", 6)
    t.gen_text(
        f"Press \x1b[94mDEL{R} to enter SETUP, \x1b[94mESC{R} to cancel Heap Test",
        t.num_rows,
    )
    for i in range(0, 524_288, 87_381):
        t.delete_row(8)
        t.gen_text(f"Heap Test: {i}K", 8, contin=True)
    t.delete_row(8)
    t.gen_text(f"Heap Test: 512MB {C_OK}OK{R}", 8, count=4, contin=True)
    t.gen_text("", 11, count=BEAT, contin=True)


def login_sequence(t: gifos.Terminal, now: str) -> None:
    t.clear_frame()
    t.clone_frame(BEAT)
    t.toggle_show_cursor(False)
    t.gen_text(f"{C_VAL}JVM OS v21.0.2 (tty1){R}", 1, count=BEAT)
    t.gen_text("login: ", 3, count=BEAT)
    t.toggle_show_cursor(True)
    t.gen_typing_text(USERNAME, 3, contin=True, speed=TYPING)
    t.gen_text("", 4, count=BEAT)
    t.toggle_show_cursor(False)
    t.gen_text("password: ", 4, count=BEAT)
    t.toggle_show_cursor(True)
    t.gen_typing_text("*********", 4, contin=True, speed=TYPING)
    t.toggle_show_cursor(False)
    t.gen_text(f"Last login: {now} on tty1", 6)


def fetch_sequence(t: gifos.Terminal) -> None:
    """Um `fetch.sh` estilo neofetch com o cartao de visita."""
    t.clear_frame()
    t.gen_prompt(1)
    prompt_col = t.curr_col
    t.clone_frame(BEAT)
    t.toggle_show_cursor(True)
    t.gen_typing_text("\x1b[91mfetch.s", 1, contin=True, speed=TYPING)
    t.delete_row(1, prompt_col)
    t.gen_text(f"{C_OK}fetch.sh{R}", 1, contin=True)
    t.gen_typing_text(f" -u {USERNAME}", 1, contin=True, speed=TYPING)
    t.toggle_show_cursor(False)

    details = f"""
    {C_HDR}{USERNAME}@GitHub{R}
    {RULE * 14}
    {C_KEY}Name:      {C_VAL}{FULL_NAME}{R}
    {C_KEY}Host:      {C_VAL}{SCHOOL}{R}
    {C_KEY}Location:  {C_VAL}{LOCATION}{R}
    {C_KEY}Backend:   {C_VAL}Java, Spring Boot, PostgreSQL{R}
    {C_KEY}Frontend:  {C_VAL}TypeScript, React, Astro{R}
    {C_KEY}IDE:       {C_VAL}IntelliJ IDEA, VS Code{R}

    {C_HDR}Currently Learning:{R}
    {RULE * 19}
    {C_VAL}Python Ecosystem{R}
    {C_VAL}Data Structures & Algorithms{R}
    {C_VAL}API Design{R}
    {C_VAL}Software Architecture{R}

    {C_HDR}Contact:{R}
    {RULE * 8}
    {C_KEY}Email:     {C_VAL}{EMAIL}{R}
    {C_KEY}Website:   {C_VAL}{WEBSITE}{R}
    {C_KEY}LinkedIn:  {C_VAL}{LINKEDIN}{R}
    """
    t.gen_text(details, 2, count=BEAT, contin=True)

    t.toggle_show_cursor(True)
    t.gen_prompt(t.curr_row)
    t.gen_typing_text(
        f"{C_OK}# Building beyond the happy path.",
        t.curr_row,
        contin=True,
        speed=TYPING,
    )
    t.gen_text("", t.curr_row, count=HOLD_FINAL, contin=True)


def update_readme() -> None:
    """Troca SO o bloco entre os marcadores, preservando o resto do README."""
    content = README.read_text(encoding="utf-8")
    block = f"""{START}
<picture>
    <source media="(prefers-color-scheme: dark)" srcset="./output.gif">
    <source media="(prefers-color-scheme: light)" srcset="./output.gif">
    <img alt="{FULL_NAME} - terminal" src="./output.gif">
</picture>

<br>
{END}"""

    pattern = re.compile(f"{re.escape(START)}.*?{re.escape(END)}", re.DOTALL)
    if not pattern.search(content):
        raise SystemExit(
            f"ERRO: marcadores {START} / {END} nao encontrados no README.md. "
            "O bloco precisa existir para ser substituido."
        )
    README.write_text(pattern.sub(lambda _: block, content), encoding="utf-8")
    print("INFO: bloco do terminal atualizado no README.md")


def main() -> None:
    now_dt = datetime.now(TIMEZONE)
    year = now_dt.strftime("%Y")
    now = now_dt.strftime("%a %b %d %I:%M:%S %p %Z %Y")

    height = YPAD * 2 + CONTENT_ROWS * ROW_H
    t = gifos.Terminal(750, height, 15, YPAD)
    t.set_prompt(PROMPT)

    boot_sequence(t, year)
    login_sequence(t, now)
    fetch_sequence(t)

    t.gen_gif()
    update_readme()


if __name__ == "__main__":
    main()
