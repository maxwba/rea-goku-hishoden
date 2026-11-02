pub mod layout;

use std::collections::BTreeMap;

pub const REQUIRED_KEYS: [&str; 22] = [
    "demo.title",
    "menu.start",
    "menu.options",
    "menu.exit",
    "demo.message",
    "menu.controls",
    "demo.next",
    "common.back",
    "options.language",
    "options.scale",
    "options.palette",
    "options.controls",
    "palette.green",
    "palette.blue",
    "palette.gray",
    "title.name",
    "title.subtitle",
    "title.demo",
    "title.start",
    "dialogue.speaker",
    "dialogue.reveal",
    "dialogue.finish",
];

pub struct Catalog(BTreeMap<String, String>);

impl Catalog {
    pub fn load(json: &str) -> Result<Self, String> {
        let values: BTreeMap<String, String> =
            serde_json::from_str(json).map_err(|error| error.to_string())?;
        for key in REQUIRED_KEYS {
            if values.get(key).is_none_or(|text| text.trim().is_empty()) {
                return Err(format!("Chave ausente ou vazia: {key}"));
            }
        }
        for key in ["options.scale", "options.palette"] {
            if values[key].matches("{value}").count() != 1 {
                return Err(format!("Marcador {{value}} inválido: {key}"));
            }
        }
        Ok(Self(values))
    }

    pub fn pt_br() -> Result<Self, String> {
        Self::load(include_str!("../../localization/pt-BR.json"))
    }

    pub fn text(&self, key: &str) -> &str {
        self.0.get(key).map(String::as_str).unwrap_or("[pendente]")
    }
}
