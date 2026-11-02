use font8x8::{UnicodeFonts, BASIC_FONTS, LATIN_FONTS};

pub fn glyph(character: char) -> Option<[u8; 8]> {
    BASIC_FONTS
        .get(character)
        .or_else(|| LATIN_FONTS.get(character))
}
