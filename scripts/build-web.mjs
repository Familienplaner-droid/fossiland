// Baut den Web-Teil der App nach www/: Spiel-HTML + Grafiken + lokale Schriften (läuft offline).
import { readFileSync, writeFileSync, mkdirSync, rmSync, cpSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const www = join(root, "www");
rmSync(www, { recursive: true, force: true });
mkdirSync(join(www, "fonts"), { recursive: true });

// Schriften aus @fontsource ins Paket kopieren
const fonts = [
  ["Lilita One", "lilita-one", 400],
  ["Atkinson Hyperlegible", "atkinson-hyperlegible", 400],
  ["Atkinson Hyperlegible", "atkinson-hyperlegible", 700],
];
const ranges = {
  latin: "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD",
  "latin-ext": "U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF",
};
let css = "";
for (const [family, pkg, weight] of fonts) {
  for (const subset of Object.keys(ranges)) {
    const file = `${pkg}-${subset}-${weight}-normal.woff2`;
    const src = join(root, "node_modules", "@fontsource", pkg, "files", file);
    if (!existsSync(src)) continue;
    cpSync(src, join(www, "fonts", file));
    css += `@font-face{font-family:"${family}";font-style:normal;font-weight:${weight};font-display:swap;src:url(${file}) format("woff2");unicode-range:${ranges[subset]}}\n`;
  }
}
writeFileSync(join(www, "fonts", "fonts.css"), css);

// Grafiken
cpSync(join(root, "src", "assets"), join(www, "assets"), { recursive: true });

// Spiel-HTML in ein vollständiges Dokument einbetten
let game = readFileSync(join(root, "src", "game.html"), "utf8");
game = game.replace(/<link rel="stylesheet" href="https:\/\/fonts\.googleapis\.com[^>]*>/, '<link rel="stylesheet" href="fonts/fonts.css">');
game = game.replace(/<meta name="claude:viewport-fit-sides"[^>]*>\n?/, "");
const cut = game.indexOf("</style>") + "</style>".length;
const html = `<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no">
<meta name="theme-color" content="#2a1c13">
<style>html{-webkit-text-size-adjust:100%;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none}:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;overscroll-behavior:none}img{max-width:100%}textarea{-webkit-user-select:text;user-select:text}</style>
${game.slice(0, cut)}
</head>
<body>
${game.slice(cut)}
</body>
</html>
`;
writeFileSync(join(www, "index.html"), html);
console.log("www/ gebaut");
