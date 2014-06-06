#!/bin/sh

echo "Generating HTML from Sphinx..."
make html

echo "Copying output files to site docs folder..."
cp build/html/*.html ../../bipolar-website/docs/
cp build/html/*.js ../../bipolar-website/docs/
cp build/html/*.inv ../../bipolar-website/docs/
cp build/html/_sources/*.txt ../../bipolar-website/docs/_sources/
cp build/html/_static/*.css ../../bipolar-website/docs/_static/
cp build/html/_static/*.js ../../bipolar-website/docs/_static/
cp build/html/_static/*.png ../../bipolar-website/docs/_static/
#cp build/html/_sources/examples/*.txt ../../bipolar-website/docs/_sources/examples/
#cp build/html/examples/*.html ../../bipolar-website/docs/examples/

echo "Done!"
