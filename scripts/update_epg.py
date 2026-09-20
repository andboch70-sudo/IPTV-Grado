import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# =========================================================
# IPTV GRADO - EPG AUTO UPDATE
# Versione 1.0
# =========================================================

SOURCE = (
    "https://epgshare01.online/epgshare01/"
    "epg_ripper_IT1.xml.gz"
)

OUTPUT = Path("EPG_Grado.xml")

# Canali per i quali vogliamo conservare la guida.
# Il confronto viene fatto anche sul nome visualizzato.
WANTED = [
    "Rai 1",
    "Rai 2",
    "Rai 3",
    "La7",
    "TV8",
    "Nove",
    "Rai 4",
    "Rai 5",
    "Rai Movie",
    "Rai Premium",
    "Cielo",
    "TV2000",
    "Real Time",
    "Food Network",
    "Discovery Channel",
    "Giallo",
    "DMAX",
    "HGTV",
    "K2",
    "Rai Gulp",
    "Rai YoYo",
    "Frisbee",
    "Super!",
    "Rai News 24",
    "Sky TG24",
    "Rai Storia",
    "Rai Scuola",
    "Rai Sport",
    "SuperTennis",
    "RTL 102.5",
    "Radio 105 TV",
    "R101 TV",
    "Deejay TV",
    "RadioItaliaTV",
    "Radio Kiss Kiss TV",
]


def normalize(text):
    return (
        text.lower()
        .replace(" ", "")
        .replace("-", "")
        .replace("_", "")
        .replace(".", "")
    )


print("Scaricamento EPG Italia...")

request = urllib.request.Request(
    SOURCE,
    headers={
        "User-Agent": "IPTV-Grado-EPG/1.0"
    },
)

with urllib.request.urlopen(
    request,
    timeout=90,
) as response:
    compressed = response.read()


# La sorgente è XML compresso gzip.
import gzip

xml_data = gzip.decompress(compressed)

print(
    "EPG scaricato:",
    round(len(xml_data) / 1024 / 1024, 2),
    "MB"
)


root = ET.fromstring(xml_data)


wanted_normalized = {
    normalize(name)
    for name in WANTED
}


selected_ids = set()


# =========================================================
# IDENTIFICA I CANALI DESIDERATI
# =========================================================

for channel in root.findall("channel"):

    channel_id = channel.get("id", "")

    names = [
        x.text or ""
        for x in channel.findall("display-name")
    ]

    matches = False

    for name in names:

        n = normalize(name)

        if n in wanted_normalized:
            matches = True
            break

    if matches:
        selected_ids.add(channel_id)

        print(
            "EPG TROVATO:",
            channel_id,
            names[0] if names else "",
        )


print(
    "Canali EPG selezionati:",
    len(selected_ids)
)


# =========================================================
# CREA XMLTV ALLEGGERITO
# =========================================================

new_root = ET.Element("tv")

# Copia i canali
for channel in root.findall("channel"):

    if channel.get("id") in selected_ids:
        new_root.append(channel)


programme_count = 0

# Copia soltanto i programmi dei canali selezionati
for programme in root.findall("programme"):

    if programme.get("channel") in selected_ids:

        new_root.append(programme)

        programme_count += 1


tree = ET.ElementTree(new_root)

ET.indent(
    tree,
    space="  ",
)


tree.write(
    OUTPUT,
    encoding="utf-8",
    xml_declaration=True,
)


size_mb = OUTPUT.stat().st_size / 1024 / 1024


print("")
print("======================================")
print("EPG GRADO GENERATO")
print("Canali:", len(selected_ids))
print("Programmi:", programme_count)
print("Dimensione:", round(size_mb, 2), "MB")
print("======================================")


# Controllo di sicurezza:
# non sostituiamo il nostro EPG con un file vuoto.
if len(selected_ids) < 10:
    raise RuntimeError(
        "Troppi pochi canali EPG trovati. "
        "Aggiornamento annullato."
    )
