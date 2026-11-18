# CV

Source for my CV, written in YAML and built with [RenderCV](https://github.com/rendercv/rendercv) (Opal theme, SUSE font).

## Download

Every change to the CV builds a fresh PDF in GitHub Actions:
**Actions → Build CV → latest run → Artifacts → George_Agriogiannis_CV**.

## Build locally

```bash
pip install "rendercv[full]==2.8"

mkdir -p fonts
base=https://raw.githubusercontent.com/google/fonts/main/ofl/suse
curl -fsSL -o 'fonts/SUSE[wght].ttf'        "$base/SUSE%5Bwght%5D.ttf"
curl -fsSL -o 'fonts/SUSE-Italic[wght].ttf' "$base/SUSE-Italic%5Bwght%5D.ttf"

rendercv render George_Agriogiannis_CV.yaml
```

The PDF lands in `rendercv_output/`. The font is fetched at build time and not stored in the repo
([SUSE font](https://fonts.google.com/specimen/SUSE), SIL Open Font License).
