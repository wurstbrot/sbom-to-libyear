# sbom-to-libyear
Provide an SBOM and generate libyear based on.

# Docker Usage
```bash
docker run -v ./sample-sboms/pip.cdx.json:/input/sbom.json:ro -v ./output:/output wurstbrot/sbom-to-libyear /input/sbom.json --report-path /output/report.json --format json
```

# Test
You can find sample SBOMs in https://github.com/anthonyharrison/sbom4python .

# Disclaimer
This code is written by the AI claude. Prompts are developed by @wurstbrot
