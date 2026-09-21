import urllib.request
import gzip
import xml.etree.ElementTree as ET
from pathlib import Path
import io


# =========================================================
# IPTV GRADO - EPG TEST
# Versione 1.0
#
# EPG ridotto per verificare il caricamento XMLTV
# su Hisense VIDAA / SS IPTV.
#
# NON modifica EPG_Grado.xml.
# Genera esclusivamente EPG_Grado_TEST.xml.
# =========================================================

SOURCE = (
    "https://epgshare01.online/"
    "epgshare01/epg_ripper_IT1.xml.gz"
)

OUTPUT = Path("EPG_Grado_TEST.xml")


# =========================================================
# CANALI TEST
# =========================================================

WANTED_IDS = {
    "Rai1.it",
    "Rai2.it",
    "Rai3.it",
    "Rete.4.it",
    "Canale.5.it",
    "Italia.1.it",
}


# =========================================================
# DOWNLOAD
# =========================================================

def download_epg():

    print("")
    print("======================================")
    print("IPTV GRADO - EPG TEST v1.0")
    print("======================================")
    print("")

    print("Scaricamento EPG sorgente...")

    request = urllib.request.Request(
        SOURCE,
        headers={
            "User-Agent": "IPTV-Grado-EPG-Test/1.0"
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=90,
    ) as response:

        compressed_data = response.read()

    print(
        "Dimensione download:",
        round(
            len(compressed_data) / 1024 / 1024,
            2,
        ),
        "MB",
    )

    print("Decompressione EPG...")

    return gzip.decompress(
        compressed_data
    )


# =========================================================
# GENERAZIONE EPG RIDOTTO
# =========================================================

def build_test_epg(xml_data):

    print("Analisi XMLTV...")

    selected_channels = []
    selected_programmes = []

    found_ids = set()

    context = ET.iterparse(
        io.BytesIO(xml_data),
        events=("end",),
    )

    for event, elem in context:

        if elem.tag == "channel":

            channel_id = elem.get("id")

            if channel_id in WANTED_IDS:

                selected_channels.append(elem)

                found_ids.add(
                    channel_id
                )

        elif elem.tag == "programme":

            channel_id = elem.get("channel")

            if channel_id in WANTED_IDS:

                selected_programmes.append(
                    elem
                )

    missing = (
        WANTED_IDS - found_ids
    )

    if missing:

        raise RuntimeError(
            "Canali EPG TEST mancanti: "
            + ", ".join(
                sorted(missing)
            )
        )

    if len(selected_channels) != 6:

        raise RuntimeError(
            "Errore: attesi 6 canali EPG TEST, "
            f"trovati {len(selected_channels)}."
        )

    if not selected_programmes:

        raise RuntimeError(
            "Errore: nessun programma trovato "
            "per i canali TEST."
        )

    print(
        "Canali selezionati:",
        len(selected_channels),
    )

    print(
        "Programmi selezionati:",
        len(selected_programmes),
    )

    root = ET.Element("tv")

    root.set(
        "generator-info-name",
        "IPTV Grado EPG TEST",
    )

    for channel in selected_channels:

        root.append(channel)

    for programme in selected_programmes:

        root.append(programme)

    tree = ET.ElementTree(root)

    ET.indent(
        tree,
        space="  ",
    )

    tree.write(
        OUTPUT,
        encoding="utf-8",
        xml_declaration=True,
    )


# =========================================================
# CONTROLLO RISULTATO
# =========================================================

def verify_output():

    if not OUTPUT.exists():

        raise RuntimeError(
            "EPG_Grado_TEST.xml non generato."
        )

    size = OUTPUT.stat().st_size

    if size < 1000:

        raise RuntimeError(
            "EPG TEST troppo piccolo."
        )

    print("")
    print(
        "Dimensione EPG TEST:",
        round(
            size / 1024,
            1,
        ),
        "KB",
    )

    print("")
    print("EPG TEST generato correttamente.")


# =========================================================
# MAIN
# =========================================================

def main():

    xml_data = download_epg()

    build_test_epg(
        xml_data
    )

    verify_output()

    print("")
    print("======================================")
    print("EPG_Grado_TEST.xml PRONTO")
    print("6 CANALI")
    print("======================================")
    print("")


if __name__ == "__main__":
    main()
