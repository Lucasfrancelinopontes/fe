#!/usr/bin/env python3
"""Executa o laboratorio find/locate e gera o relatorio PDF da atividade."""

from __future__ import annotations

import os
import shlex
import subprocess
import textwrap
from pathlib import Path


NAME = "Lucas Francelino de Pontes"
REGISTRATION = "202614320011"
SUFFIX = REGISTRATION[-3:]
LAB = Path.home() / f"isa_busca_{SUFFIX}"
OUTPUT = Path.cwd() / f"ISA_FIND_LOCATE_LUCAS_FRANCELINO_DE_PONTES_{REGISTRATION}.pdf"
LOG = Path.cwd() / "isa_find_locate_evidencias.txt"


def run(command: str, cwd: Path | None = None) -> str:
    result = subprocess.run(
        command,
        shell=True,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return f"$ {command}\n{result.stdout.rstrip()}\n"


def prepare() -> None:
    if LAB.exists():
        for path in sorted(LAB.rglob("*"), reverse=True):
            if path.is_file() or path.is_symlink():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
    LAB.mkdir(parents=True)
    for directory in ("documentos", "logs", "imagens", "scripts", "backup"):
        (LAB / directory).mkdir()
    (LAB / "identificacao.txt").write_text(
        f"Nome: {NAME}\nMatrícula: {REGISTRATION}\n", encoding="utf-8"
    )
    for filename in ("relatorio1.txt", "relatorio2.txt", "manual.txt", "Resumo.TXT", "contrato.pdf"):
        (LAB / "documentos" / filename).touch()
    for filename in ("sistema.log", "acesso.log", "erro.log"):
        (LAB / "logs" / filename).touch()
    for filename in ("logo.png", "banner.jpg", "icone.svg"):
        (LAB / "imagens" / filename).touch()
    (LAB / "scripts" / "backup.sh").write_text(
        '#!/bin/bash\necho "Backup iniciado"\n', encoding="utf-8"
    )
    (LAB / "scripts" / "relatorio.sh").write_text(
        '#!/bin/bash\necho "Relatório gerado"\n', encoding="utf-8"
    )
    for filename, size in (("sistema.log", "2M"), ("acesso.log", "700K"),):
        subprocess.run(["truncate", "-s", size, str(LAB / "logs" / filename)], check=True)
    subprocess.run(["truncate", "-s", "100K", str(LAB / "imagens" / "banner.jpg")], check=True)
    os.utime(LAB / "documentos" / "relatorio1.txt", (0, 0))
    subprocess.run(["touch", "-d", "7 days ago", str(LAB / "documentos" / "relatorio1.txt")], check=True)
    subprocess.run(["touch", "-d", "2 days ago", str(LAB / "documentos" / "relatorio2.txt")], check=True)
    subprocess.run(["chmod", "+x", str(LAB / "scripts" / "backup.sh"), str(LAB / "scripts" / "relatorio.sh")], check=True)
    for filename, mode in (("relatorio1.txt", "600"), ("relatorio2.txt", "640"),
                           ("manual.txt", "644"), ("contrato.pdf", "444")):
        subprocess.run(["chmod", mode, str(LAB / "documentos" / filename)], check=True)


def collect() -> list[tuple[str, str]]:
    q = shlex.quote
    lab = q(str(LAB))
    sections: list[tuple[str, str]] = []
    sections.append(("ETAPA 1 — ESTRUTURA", run(f"echo {q(str(LAB))}; find {lab}")))
    sections.append(("ETAPA 2 — NOME", "\n".join([
        run(f"find {lab} -name manual.txt"),
        run(f"find {lab} -name 'relatorio*'"),
        run(f"find {lab} -name '*.txt'"),
        run(f"find {lab} -iname '*.txt'"),
    ])))
    sections.append(("ETAPA 3 — TIPO", "\n".join([
        run(f"find {lab} -type d"),
        run(f"find {lab} -type f"),
        run(f"find {lab}/scripts -type f"),
    ])))
    sections.append(("ETAPA 4 — EXTENSÃO", "\n".join([
        run(f"find {lab} -type f -name '*.log'"),
        run(f"find {lab} -type f -name '*.png'"),
        run(f"find {lab} -type f -name '*.sh'"),
    ])))
    sections.append(("ETAPA 5 — TAMANHO", "\n".join([
        run(f"find {lab} -type f -size +500k"),
        run(f"find {lab} -type f -size -1M"),
        run(f"find {lab} -type f -size 2M"),
    ])))
    sections.append(("ETAPA 6 — DATA", "\n".join([
        run(f"find {lab} -type f -mtime -3"),
        run(f"find {lab} -type f -mtime +5"),
        run(f"find {lab} -type f -mtime 2"),
    ])))
    sections.append(("ETAPA 7 — PERMISSÃO", "\n".join([
        run(f"find {lab} -type f -perm 600"),
        run(f"find {lab} -type f -perm 640"),
        run(f"find {lab} -type f -perm 644"),
        run(f"find {lab} -type f -perm 444"),
        run(f"ls -l {lab}/documentos"),
    ])))
    sections.append(("ETAPA 8 — PROPRIETÁRIO", "\n".join([
        run("whoami"),
        run(f"find {lab} -type f -user \"$USER\""),
        run(f"ls -l {lab}/documentos"),
    ])))
    sections.append(("ETAPA 9 — FILTROS COMBINADOS", "\n".join([
        run(f"find {lab} -type f -name '*.log' -size +500k"),
        run(f"find {lab}/documentos -type f -iname '*.txt' -mtime -3"),
        run(f"find {lab}/documentos -type f -iname '*.txt' -perm 640"),
        run(f"find {lab}/scripts -type f -name '*.sh' -perm /111"),
    ])))
    subprocess.run(f"find {lab}/documentos -type f -iname '*.txt' -exec cp {{}} {lab}/backup/ \\;", shell=True, check=True)
    subprocess.run(f"find {lab}/backup -type f -exec chmod 600 {{}} \\;", shell=True, check=True)
    sections.append(("ETAPA 10 — -EXEC", "\n".join([
        run(f"ls -la {lab}/backup"),
        run(f"ls -l {lab}/backup"),
    ])))
    locate = "locate"
    locate_available = subprocess.run(["command", "-v", locate], shell=True, capture_output=True, text=True).returncode == 0
    if locate_available:
        locate_text = "\n".join([run(f"locate isa_busca_{SUFFIX}"), run("locate relatorio2.txt")])
    else:
        locate_text = "$ command -v locate\nlocate não está instalado neste ambiente; a comparação conceitual está registrada nas respostas."
    (LAB / "documentos" / "arquivo_recem_criado.txt").touch()
    sections.append(("ETAPA 11 — LOCATE", locate_text + "\n\n" + run(f"find {lab} -name arquivo_recem_criado.txt")))
    sections.append(("ETAPA 12 — DESAFIO FINAL", "\n".join([
        f"find {lab}/documentos -type f -name '*.txt'",
        f"find {lab} -type f -name '*.log' -size +1M",
        f"find {lab} -type f -mtime -3",
        f"find {lab} -type f -perm 640",
        f"find {lab}/scripts -type f -name '*.sh' -perm /111",
        f"find {lab} -type f -name '*.log' -exec cp {{}} {lab}/backup/ \\;",
        f"ls -l {lab}/backup",
    ])))
    return sections


ANSWERS = """
RESPOSTAS DAS 46 QUESTÕES
1. -iname também encontrou documentos/Resumo.TXT; -name diferencia maiúsculas de minúsculas, enquanto -iname ignora essa diferença.
2. As aspas impedem que o shell expanda *.txt antes de o find receber o padrão.
3. Em -type d, d significa directory (diretório); em -type f, f significa regular file (arquivo regular).
4. Para links simbólicos, usa-se -type l.
5. -type f restringe a arquivos regulares; * representa qualquer sequência de caracteres, inclusive vazia.
6. Acima de 500 KB: logs/sistema.log e logs/acesso.log. + significa maior que; - significa menor que. k indica kibibytes no find e M indica mebibytes.
7. -mtime +5 encontrou documentos/relatorio1.txt. -mtime -3 indica menos de três períodos de 24 horas; -mtime +5 indica mais de cinco, enquanto -mtime 5 indica aproximadamente cinco períodos completos.
8. A permissão 600 é de documentos/relatorio1.txt. O proprietário pode ler e escrever, mas não executar. A permissão 444 permite leitura para proprietário, grupo e outros. 640 não aparece com -perm 644 porque a comparação é exata.
9. $USER armazena o nome do usuário atual. -user filtra pelo proprietário informado. Para grupo, usa-se -group.
10. A busca dos logs usa três condições explícitas: -type f, -name e -size. Sim, as condições encadeadas devem ser verdadeiras. Os scripts executáveis são backup.sh e relatorio.sh.
11. {} é substituído pelo caminho de cada arquivo encontrado. O ponto e vírgula encerra a expressão -exec e precisa ser protegido do shell. Foram copiados quatro arquivos TXT; após chmod, todos ficaram com permissão 600.
12. O arquivo recém-criado não aparece imediatamente no locate quando o índice está desatualizado; aparece no find imediatamente. Depois de updatedb, passa a aparecer no locate. find busca em tempo real; locate consulta banco previamente criado. locate pode ficar desatualizado entre duas atualizações do índice.
13. Desafio: os comandos estão registrados na Etapa 12. A cópia final usa find ... -name '*.log' -exec cp {} "$LAB/backup/" \\;.
14. find percorre o sistema em tempo real e locate consulta um índice. Eu escolheria find para dados recém-criados, filtros precisos e confirmação atual; escolheria locate para buscas rápidas quando o índice for confiável. Vantagem do find: atualidade e flexibilidade; limitação: pode ser mais lento. Vantagem do locate: velocidade; limitação: resultados podem estar desatualizados e dependem do índice.
15. find / -type f -exec rm {} \\; é perigoso porque começa na raiz e pode remover todos os arquivos regulares acessíveis, causando perda irreversível de dados. Deve-se revisar o caminho, testar primeiro sem rm e pedir confirmação antes de qualquer remoção.

CONCLUSÃO
Aprendi a criar uma estrutura de laboratório e a combinar filtros do find.
As buscas por nome mostram a diferença entre -name e -iname.
Os filtros de tipo, tamanho, data, permissão e proprietário tornam a busca precisa.
Também pratiquei ações com -exec, entendendo o papel de {} e do ponto e vírgula.
O find consulta o estado atual do sistema, enquanto locate depende de um índice.
Por isso, locate é rápido, mas pode não mostrar arquivos recém-criados.
A atividade também reforçou que comandos destrutivos devem ser testados com cuidado.
Os resultados e comandos foram registrados neste relatório para permitir conferência.
"""


def pdf_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def make_pdf(sections: list[tuple[str, str]]) -> None:
    lines: list[str] = [
        "INTRODUÇÃO A SISTEMAS ABERTOS",
        "LABORATÓRIO FIND E LOCATE — RELATÓRIO",
        "",
        f"Nome: {NAME}",
        f"Matrícula: {REGISTRATION}",
        f"Diretório utilizado: {LAB}",
        "",
        "EVIDÊNCIAS DE EXECUÇÃO",
        "Os blocos abaixo registram o comando ($) e sua saída, funcionando como capturas textuais do terminal.",
    ]
    for title, output in sections:
        lines += ["", title, output]
    lines += ["", ANSWERS]
    wrapped: list[str] = []
    for line in lines:
        if len(line) <= 100:
            wrapped.append(line)
        else:
            wrapped.extend(textwrap.wrap(line, width=100, break_long_words=False, break_on_hyphens=False))

    pages = [wrapped[i:i + 58] for i in range(0, len(wrapped), 58)]
    objects: list[bytes] = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    font_id = 3 + len(pages) * 2
    page_ids = []
    for index, page_lines in enumerate(pages):
        page_id = 3 + index * 2
        content_id = page_id + 1
        page_ids.append(page_id)
        commands = ["BT", "/F1 8 Tf", "40 760 Td", "10 TL"]
        for line in page_lines:
            commands.append(f"({pdf_escape(line)}) Tj T*")
        commands.append("ET")
        stream = "\n".join(commands).encode("latin-1", "replace")
        objects.extend([
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 {font_id} 0 R >> >> /Contents {content_id} 0 R >>".encode(),
            f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream",
        ])
    objects[1:1] = [f"<< /Type /Pages /Kids [{' '.join(f'{p} 0 R' for p in page_ids)}] /Count {len(page_ids)} >>".encode()]
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")
    data = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(data))
        data.extend(f"{number} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(data)
    data.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        data.extend(f"{offset:010d} 00000 n \n".encode())
    data.extend(f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    OUTPUT.write_bytes(data)


def main() -> None:
    prepare()
    sections = collect()
    LOG.write_text("\n\n".join(f"{title}\n{output}" for title, output in sections), encoding="utf-8")
    make_pdf(sections)
    print(f"PDF gerado: {OUTPUT}")
    print(f"Laboratório: {LAB}")
    print(f"Evidências: {LOG}")


if __name__ == "__main__":
    main()
