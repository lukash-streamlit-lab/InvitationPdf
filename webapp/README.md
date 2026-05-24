# Webový Generátor PDF

Samostatná webová verze generátoru pozvánek. Původní `generator.py` v kořeni repozitáře zůstává beze změn.

## Lokální spuštění

```bash
cd webapp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Pokud aplikaci spouštíte z kořene repozitáře, použijte:

```bash
streamlit run webapp/app.py
```

Na systémech bez knihoven pro WeasyPrint je potřeba doinstalovat balíčky z `packages.txt`.
Pro Streamlit Cloud musí být tento soubor v kořeni repozitáře; `webapp/packages.txt`
je jen kopie pro lokální práci s webovou částí.

## Streamlit Community Cloud

Nejjednodušší free hosting pro tuto aplikaci je Streamlit Community Cloud:

- oficiální služba pro Streamlit aplikace,
- nasazuje přímo z GitHub repozitáře,
- pro tento projekt umí použít `webapp/requirements.txt`,
- systémové knihovny pro WeasyPrint načte z `packages.txt` v kořeni repozitáře.

Oficiální dokumentace:

- Streamlit Community Cloud: <https://docs.streamlit.io/deploy/streamlit-community-cloud>
- Deploy aplikace: <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy>
- Závislosti aplikace: <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies>

### Příprava repozitáře

Před deployem ověřte, že jsou změny nahrané v GitHub repozitáři. Streamlit Cloud aplikaci spustí z GitHubu, ne z lokální složky.

Protože WeasyPrint potřebuje systémové knihovny, musí být v kořeni repozitáře soubor `packages.txt`.
Streamlit Cloud ho použije při buildu pro instalaci apt balíčků jako Pango, Harfbuzz a fonty.
GLib runtime se nainstaluje jako systémová závislost těchto balíčků.
Změny nahrajte například takto:

```bash
git add webapp packages.txt
git commit -m "add web pdf generator app"
git push
```

`webapp/requirements.txt` může zůstat v `webapp/`, protože je vedle vstupního souboru aplikace `webapp/app.py`.
Při vytváření aplikace v Advanced settings zvolte Python 3.12.

### Deploy krok za krokem

1. Otevřete <https://share.streamlit.io/>.
2. Přihlaste se GitHub účtem.
3. Klikněte na **Create app**.
4. Vyberte GitHub repozitář a branch, typicky `main`.
5. Jako hlavní soubor aplikace nastavte:

```text
webapp/app.py
```

6. Spusťte deploy.
7. Po dokončení dostanete veřejnou URL ve tvaru `https://...streamlit.app`.

### Po deployi

- Pokud build spadne na WeasyPrint/Pango/GLib/fonty, zkontrolujte, že `packages.txt` je opravdu v kořeni repozitáře.
- Pokud build spadne na Python import, zkontrolujte `webapp/requirements.txt`.
- Nové změny aplikace nasadíte běžně přes `git push`.

### Alternativa: Hugging Face Spaces

Hugging Face Spaces také nabízí free hosting demo aplikací. Pro Streamlit ale aktuální dokumentace doporučuje použít Docker SDK a Streamlit template, protože vestavěný Streamlit SDK je označený jako deprecated. Pro tento projekt je proto jednodušší začít se Streamlit Community Cloud.

Dokumentace:

- Hugging Face Spaces: <https://huggingface.co/docs/hub/main/spaces>
- Streamlit na Spaces: <https://huggingface.co/docs/hub/main/spaces-sdks-streamlit>

## Nahrání šablony

Nahrajte buď přímo `.html` nebo `.htm` soubor, nebo ZIP se šablonou.

Přímé HTML funguje pro inline CSS, `data:` obrázky a Jinja proměnné z CSV. Pokud šablona používá relativní obrázky nebo fonty, nahrajte ZIP, který obsahuje HTML i tyto soubory. ZIP musí obsahovat alespoň jeden `.html` nebo `.htm` soubor. Externí URL jsou blokované.

CSV nebo Excel sloupce jsou přímo Jinja proměnné v šabloně. CSV může používat oddělovač `|`, `,`, `;` nebo tabulátor. U Excelu jsou podporované `.xlsx` a `.xlsm` soubory; pokud má sešit více listů, aplikace nabídne výběr listu. Příklad:

```jinja2
{{ fullName }}
{{ eventDate }}
```
