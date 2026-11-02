use crate::localization::layout;
use std::time::Duration;

/// Apresentação própria da demo. Este intervalo não foi recuperado do cartucho.
const CHARACTER_INTERVAL_NS: u128 = 30_000_000;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Advance {
    Revealed,
    NextPage,
    Finished,
}

#[derive(Debug)]
pub struct Dialogue {
    pages: Vec<Vec<String>>,
    page: usize,
    visible: usize,
    elapsed: Duration,
}

impl Default for Dialogue {
    fn default() -> Self {
        Self {
            pages: vec![vec![String::new()]],
            page: 0,
            visible: 0,
            elapsed: Duration::ZERO,
        }
    }
}

impl Dialogue {
    pub fn new(text: &str, columns: usize, rows: usize) -> Result<Self, String> {
        Ok(Self {
            pages: layout::pages(text, columns, rows)?,
            ..Self::default()
        })
    }

    pub fn page_index(&self) -> usize {
        self.page
    }

    pub fn page_count(&self) -> usize {
        self.pages.len()
    }

    fn character_count(&self) -> usize {
        self.pages[self.page]
            .iter()
            .map(|line| line.chars().count())
            .sum()
    }

    pub fn fully_revealed(&self) -> bool {
        self.visible == self.character_count()
    }

    pub fn is_last_page(&self) -> bool {
        self.page + 1 == self.pages.len()
    }

    pub fn tick(&mut self, delta: Duration) {
        if self.fully_revealed() {
            self.elapsed = Duration::ZERO;
            return;
        }
        self.elapsed = self.elapsed.saturating_add(delta);
        let remaining = self.character_count() - self.visible;
        let count = (self.elapsed.as_nanos() / CHARACTER_INTERVAL_NS).min(remaining as u128);
        self.visible += count as usize;
        let remainder = self.elapsed.as_nanos() % CHARACTER_INTERVAL_NS;
        self.elapsed = if self.fully_revealed() {
            Duration::ZERO
        } else {
            Duration::from_nanos(remainder as u64)
        };
    }

    pub fn visible_lines(&self) -> Vec<String> {
        let mut remaining = self.visible;
        self.pages[self.page]
            .iter()
            .map(|line| {
                let text: String = line.chars().take(remaining).collect();
                remaining = remaining.saturating_sub(text.chars().count());
                text
            })
            .collect()
    }

    pub fn advance(&mut self) -> Advance {
        self.elapsed = Duration::ZERO;
        if !self.fully_revealed() {
            self.visible = self.character_count();
            Advance::Revealed
        } else if !self.is_last_page() {
            self.page += 1;
            self.visible = 0;
            Advance::NextPage
        } else {
            Advance::Finished
        }
    }

    pub fn previous(&mut self) {
        if self.page > 0 {
            self.page -= 1;
            self.visible = self.character_count();
            self.elapsed = Duration::ZERO;
        }
    }

    pub fn reset(&mut self) {
        self.page = 0;
        self.visible = 0;
        self.elapsed = Duration::ZERO;
    }
}
