/// Divide texto UTF-8 por palavras. Palavras maiores que a largura são quebradas
/// por caracteres, nunca por bytes. Newlines explícitos e linhas vazias são mantidos.
pub fn wrap(text: &str, columns: usize) -> Result<Vec<String>, String> {
    if columns == 0 {
        return Err("A largura do texto precisa ser positiva".into());
    }
    let mut lines = Vec::new();
    for paragraph in text.split('\n') {
        let mut line = String::new();
        let mut length = 0;
        for word in paragraph.split_whitespace() {
            let word_length = word.chars().count();
            if length > 0 && length + 1 + word_length > columns {
                lines.push(std::mem::take(&mut line));
                length = 0;
            }
            if length > 0 {
                line.push(' ');
                length += 1;
            }
            for character in word.chars() {
                if length == columns {
                    lines.push(std::mem::take(&mut line));
                    length = 0;
                }
                line.push(character);
                length += 1;
            }
        }
        lines.push(line);
    }
    Ok(lines)
}

pub fn pages(text: &str, columns: usize, rows: usize) -> Result<Vec<Vec<String>>, String> {
    if rows == 0 {
        return Err("A altura do texto precisa ser positiva".into());
    }
    Ok(wrap(text, columns)?
        .chunks(rows)
        .map(|chunk| chunk.to_vec())
        .collect())
}
