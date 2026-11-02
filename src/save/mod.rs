use crate::settings::DisplaySettings;
use serde::{Deserialize, Serialize};
use std::fs::{self, OpenOptions};
use std::io::{Read, Write};
use std::path::Path;

const MAX_SAVE_BYTES: u64 = 4096;

/// Preferências próprias da demonstração, sem relação com saves do cartucho.
#[derive(Debug, Default, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct DemoPreferences {
    pub selected_menu: usize,
    #[serde(default)]
    pub display: DisplaySettings,
}

impl DemoPreferences {
    pub fn validate(&self) -> Result<(), String> {
        if self.selected_menu >= 3 {
            return Err("Seleção de menu inválida no arquivo de preferências".into());
        }
        self.display.validate()
    }

    pub fn load(path: &Path) -> Result<Self, String> {
        let file = match fs::File::open(path) {
            Ok(file) => file,
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
                return Ok(Self::default());
            }
            Err(error) => return Err(error.to_string()),
        };
        let mut bytes = Vec::new();
        file.take(MAX_SAVE_BYTES + 1)
            .read_to_end(&mut bytes)
            .map_err(|error| error.to_string())?;
        if bytes.len() as u64 > MAX_SAVE_BYTES {
            return Err("Arquivo de preferências excede o limite de tamanho".into());
        }
        let value: Self = serde_json::from_slice(&bytes).map_err(|error| error.to_string())?;
        value.validate()?;
        Ok(value)
    }

    /// Escrita em arquivo temporário no mesmo diretório e substituição por rename.
    /// create_new impede sobrescrever um temporário pertencente a outra instância.
    pub fn store(&self, path: &Path) -> Result<(), String> {
        self.validate()?;
        let parent = path
            .parent()
            .filter(|p| !p.as_os_str().is_empty())
            .unwrap_or(Path::new("."));
        fs::create_dir_all(parent).map_err(|error| error.to_string())?;
        let name = path.file_name().ok_or("Nome de arquivo inválido")?;
        let mut temporary_name = name.to_os_string();
        temporary_name.push(format!(".{}.tmp", std::process::id()));
        let temporary_path = parent.join(temporary_name);
        let mut file = OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&temporary_path)
            .map_err(|error| error.to_string())?;
        let result = (|| {
            let bytes = serde_json::to_vec_pretty(self).map_err(|error| error.to_string())?;
            file.write_all(&bytes).map_err(|error| error.to_string())?;
            file.sync_all().map_err(|error| error.to_string())?;
            drop(file);
            fs::rename(&temporary_path, path).map_err(|error| error.to_string())
        })();
        if result.is_err() {
            let _ = fs::remove_file(&temporary_path);
        }
        result
    }
}
