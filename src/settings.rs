use serde::{Deserialize, Serialize};

#[derive(Clone, Copy, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub enum Palette {
    #[default]
    Green,
    Blue,
    Gray,
}

impl Palette {
    pub fn cycle(self, forward: bool) -> Self {
        match (self, forward) {
            (Self::Green, true) | (Self::Gray, false) => Self::Blue,
            (Self::Blue, true) | (Self::Green, false) => Self::Gray,
            (Self::Gray, true) | (Self::Blue, false) => Self::Green,
        }
    }

    pub fn localization_key(self) -> &'static str {
        match self {
            Self::Green => "palette.green",
            Self::Blue => "palette.blue",
            Self::Gray => "palette.gray",
        }
    }

    /// Cores próprias da demonstração, sem extrair paletas do cartucho.
    pub fn colors(self) -> ([u8; 3], [u8; 3]) {
        match self {
            Self::Green => ([20, 35, 40], [220, 240, 200]),
            Self::Blue => ([20, 25, 55], [190, 225, 255]),
            Self::Gray => ([25, 25, 25], [235, 235, 235]),
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct DisplaySettings {
    pub scale: u8,
    pub palette: Palette,
}

impl Default for DisplaySettings {
    fn default() -> Self {
        Self {
            scale: 4,
            palette: Palette::Green,
        }
    }
}

impl DisplaySettings {
    pub fn validate(self) -> Result<(), String> {
        if !(2..=6).contains(&self.scale) {
            return Err("A escala precisa estar entre 2x e 6x".into());
        }
        Ok(())
    }

    pub fn cycle_scale(&mut self, forward: bool) {
        self.scale = if forward {
            if self.scale >= 6 {
                2
            } else {
                self.scale + 1
            }
        } else if self.scale <= 2 {
            6
        } else {
            self.scale - 1
        };
    }
}
