import fitz
import re
import csv


def extract_text_from_pdf(pdf_path, password=None):
    doc = fitz.open(pdf_path)
    if doc.needs_pass and password:
        doc.authenticate(password)

    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"

    doc.close()
    return text


def extract_details(text, keyword="Detalhamento da Fatura"):
    start_index = text.find(keyword)
    if start_index == -1:
        return []

    details_text = text[start_index:]

    end_index = details_text.find("Parcelamentos")
    details_text = details_text[end_index:]

    pattern = re.compile(
        r'(\d{2}/\d{2})\s([A-Za-z\s.\-0-9*#@&!+=~_]+)\s*(\d{2}/\d{2})?\s([-+]?[0-9]*,?[0-9]+(?:\.[0-9]{1,2})?)'
    )

    matches = re.findall(pattern, details_text)

    details = []
    for match in matches:
        data = match[0]
        descricao = match[1].strip()
        parcela = match[2] if match[2] else ''
        valor = match[3].replace(',', '.')

        try:
            valor_float = float(valor.replace(',', '.'))
            if valor_float < 0:
                continue
        except ValueError:
            continue

        valor_formatado = f"R$ {valor_float:,.2f}".replace(",", ";").replace(".", ",")

        details.append([data, descricao, parcela, valor_formatado])

    return details


def save_to_csv(details, filename="fatura.csv"):
    headers = ["Data", "Descrição", "Parcela", "R$"]
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(details)

    print(f"Arquivo CSV gerado com sucesso: {filename}")


# Insira de acordo com suas informações
pdf_path = r""
password = ""

texto_extraido = extract_text_from_pdf(pdf_path, password)

detalhamento = extract_details(texto_extraido)

save_to_csv(detalhamento)
