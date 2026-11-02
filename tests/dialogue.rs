use rea_goku_hishoden::scenes::dialogue::{Advance, Dialogue};
use rea_goku_hishoden::scenes::{Action, App, Scene};
use std::time::Duration;

#[test]
fn title_requires_start_before_showing_menu() {
    let mut app = App::default();
    assert_eq!(app.scene, Scene::Title);
    app.handle(Action::Down);
    assert_eq!(app.scene, Scene::Title);
    assert!(app.handle(Action::Start));
    assert_eq!(app.scene, Scene::Menu);
    assert_eq!(app.menu.selected(), 0);
}

#[test]
fn progressive_text_preserves_unicode_and_time_remainder() {
    let mut dialogue = Dialogue::new("Ação", 18, 6).unwrap();
    dialogue.tick(Duration::from_millis(29));
    assert_eq!(dialogue.visible_lines(), [""]);
    dialogue.tick(Duration::from_millis(2));
    assert_eq!(dialogue.visible_lines(), ["A"]);
    dialogue.tick(Duration::from_millis(59));
    assert_eq!(dialogue.visible_lines(), ["Açã"]);
    dialogue.tick(Duration::MAX);
    assert_eq!(dialogue.visible_lines(), ["Ação"]);
    assert!(dialogue.fully_revealed());
}

#[test]
fn confirmation_reveals_before_advancing_and_stops_at_the_end() {
    let mut dialogue = Dialogue::new("um\ndois\ntrês", 8, 2).unwrap();
    assert_eq!(dialogue.advance(), Advance::Revealed);
    assert_eq!(dialogue.visible_lines(), ["um", "dois"]);
    assert_eq!(dialogue.advance(), Advance::NextPage);
    assert_eq!(dialogue.visible_lines(), [""]);
    assert_eq!(dialogue.advance(), Advance::Revealed);
    assert_eq!(dialogue.visible_lines(), ["três"]);
    assert_eq!(dialogue.advance(), Advance::Finished);
    dialogue.previous();
    assert_eq!(dialogue.page_index(), 0);
    assert_eq!(dialogue.visible_lines(), ["um", "dois"]);
    dialogue.reset();
    assert_eq!(dialogue.visible_lines(), ["", ""]);
}

#[test]
fn dialogue_finishes_to_menu_and_reopens_from_beginning() {
    let mut app = App::new(Dialogue::new("Olá!", 18, 6).unwrap());
    app.handle(Action::Start);
    app.handle(Action::Confirm);
    app.tick(Duration::from_secs(1));
    assert!(app.dialogue.fully_revealed());
    app.handle(Action::Confirm);
    assert_eq!(app.scene, Scene::Menu);
    app.handle(Action::Confirm);
    assert_eq!(app.scene, Scene::Example);
    assert!(!app.dialogue.fully_revealed());
    app.handle(Action::Back);
    app.tick(Duration::from_secs(1));
    assert!(!app.dialogue.fully_revealed());
}

#[test]
fn blank_dialogue_and_empty_lines_are_safe() {
    let mut dialogue = Dialogue::new("\n\n", 18, 2).unwrap();
    assert_eq!(dialogue.advance(), Advance::NextPage);
    assert_eq!(dialogue.advance(), Advance::Finished);
    assert!(Dialogue::new("texto", 0, 2).is_err());
}
