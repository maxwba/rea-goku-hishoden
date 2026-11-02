pub mod dialogue;

use crate::settings::DisplaySettings;
use dialogue::{Advance, Dialogue};
use std::time::Duration;

#[derive(Default, Debug, PartialEq, Eq)]
pub enum Scene {
    #[default]
    Title,
    Menu,
    Example,
    Options,
}

#[derive(Default)]
pub struct Menu {
    selected: usize,
}

impl Menu {
    pub fn selected(&self) -> usize {
        self.selected
    }

    pub fn restore(&mut self, selected: usize) -> Result<(), String> {
        if selected >= 3 {
            return Err("Seleção de menu inválida".into());
        }
        self.selected = selected;
        Ok(())
    }

    pub fn next(&mut self) {
        self.selected = (self.selected + 1).min(2);
    }

    pub fn previous(&mut self) {
        self.selected = self.selected.saturating_sub(1);
    }
}

pub enum Action {
    Up,
    Down,
    Confirm,
    Start,
    Back,
    Left,
    Right,
}

#[derive(Default)]
pub struct App {
    pub menu: Menu,
    pub scene: Scene,
    pub dialogue: Dialogue,
    pub option: usize,
    pub display: DisplaySettings,
}

impl App {
    pub fn new(dialogue: Dialogue) -> Self {
        Self {
            dialogue,
            ..Self::default()
        }
    }

    pub fn tick(&mut self, delta: Duration) {
        if self.scene == Scene::Example {
            self.dialogue.tick(delta);
        }
    }

    fn adjust_option(&mut self, forward: bool) {
        if self.option == 0 {
            self.display.cycle_scale(forward);
        } else {
            self.display.palette = self.display.palette.cycle(forward);
        }
    }

    /// Retorna false quando o usuário pede para encerrar.
    pub fn handle(&mut self, action: Action) -> bool {
        match (&self.scene, action) {
            (Scene::Title, Action::Start) => self.scene = Scene::Menu,
            (Scene::Title, Action::Back) => return false,
            (Scene::Menu, Action::Up) => self.menu.previous(),
            (Scene::Menu, Action::Down) => self.menu.next(),
            (Scene::Menu, Action::Confirm | Action::Start) => {
                self.dialogue.reset();
                self.scene = match self.menu.selected() {
                    0 => Scene::Example,
                    1 => Scene::Options,
                    _ => return false,
                };
            }
            (Scene::Menu, Action::Back) => return false,
            (_, Action::Back) => {
                self.scene = Scene::Menu;
                self.dialogue.reset();
            }
            (Scene::Example, Action::Confirm | Action::Start | Action::Right) => {
                if self.dialogue.advance() == Advance::Finished {
                    self.scene = Scene::Menu;
                }
            }
            (Scene::Example, Action::Left) => self.dialogue.previous(),
            (Scene::Options, Action::Up | Action::Down) => {
                self.option = (self.option + 1) % 2;
            }
            (Scene::Options, Action::Right | Action::Confirm | Action::Start) => {
                self.adjust_option(true);
            }
            (Scene::Options, Action::Left) => {
                self.adjust_option(false);
            }
            _ => {}
        }
        true
    }
}
