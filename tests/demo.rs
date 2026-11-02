use rea_goku_hishoden::{
    assets,
    localization::{Catalog, REQUIRED_KEYS},
    save::DemoPreferences,
    scenes::Menu,
};

#[test]
fn catalog_and_font_cover_all_demo_strings() {
    let catalog = Catalog::pt_br().unwrap();
    for key in REQUIRED_KEYS {
        for character in catalog.text(key).chars().filter(|c| *c != '\n') {
            assert!(
                assets::glyph(character).is_some(),
                "Glifo ausente: {character}"
            );
        }
    }
    assert!(Catalog::load("{}").is_err());
}

#[test]
fn selection_contract_has_three_positions_and_stops_at_both_ends() {
    // Contrato C-001: sequência própria, sem ROM ou estado extraído nas fixtures.
    use rea_goku_hishoden::scenes::{Action, App};
    let mut app = App::default();
    app.handle(rea_goku_hishoden::scenes::Action::Start);
    for (action, expected) in [
        (Action::Up, 0),
        (Action::Down, 1),
        (Action::Down, 2),
        (Action::Down, 2),
        (Action::Up, 1),
        (Action::Up, 0),
        (Action::Up, 0),
    ] {
        assert!(app.handle(action));
        assert_eq!(app.menu.selected(), expected);
    }
}

#[test]
fn preferences_round_trip() {
    let value = DemoPreferences {
        selected_menu: 2,
        ..Default::default()
    };
    let json = serde_json::to_string(&value).unwrap();
    assert_eq!(
        serde_json::from_str::<DemoPreferences>(&json).unwrap(),
        value
    );
}

#[test]
fn text_wraps_without_splitting_utf8_or_losing_blank_lines() {
    use rea_goku_hishoden::localization::layout::{pages, wrap};
    assert_eq!(wrap("ação e união", 6).unwrap(), ["ação e", "união"]);
    assert_eq!(wrap("áéíóú", 2).unwrap(), ["áé", "íó", "ú"]);
    assert_eq!(wrap("um\n\ndois", 8).unwrap(), ["um", "", "dois"]);
    assert_eq!(pages("um\ndois\ntrês", 8, 2).unwrap().len(), 2);
    assert!(wrap("texto", 0).is_err());
    assert!(pages("texto", 8, 0).is_err());
}

#[test]
fn scene_navigation_limits_pages_and_restores_menu() {
    use rea_goku_hishoden::scenes::dialogue::Dialogue;
    use rea_goku_hishoden::scenes::{Action, App, Scene};
    let mut app = App::new(Dialogue::new("um\ndois\ntrês", 8, 2).unwrap());
    app.handle(Action::Start);
    assert!(app.handle(Action::Confirm));
    assert_eq!(app.scene, Scene::Example);
    app.handle(Action::Confirm); // Primeiro revela, sem pular página.
    assert_eq!(app.dialogue.page_index(), 0);
    app.handle(Action::Confirm);
    assert_eq!(app.dialogue.page_index(), 1);
    app.handle(Action::Left);
    app.handle(Action::Left);
    assert_eq!(app.dialogue.page_index(), 0);
    app.handle(Action::Back);
    assert_eq!(app.scene, Scene::Menu);
    app.handle(Action::Down);
    app.handle(Action::Confirm);
    assert_eq!(app.scene, Scene::Options);
    app.handle(Action::Back);
    assert_eq!(app.menu.selected(), 1);
    app.handle(Action::Down);
    assert!(!app.handle(Action::Confirm));
}

#[test]
fn invalid_preferences_are_rejected() {
    assert!(DemoPreferences {
        selected_menu: 3,
        ..Default::default()
    }
    .validate()
    .is_err());
    let mut menu = Menu::default();
    assert!(menu.restore(usize::MAX).is_err());
    assert_eq!(menu.selected(), 0);
}

#[test]
fn disk_preferences_round_trip_and_reject_corruption() {
    use std::fs;
    use std::sync::atomic::{AtomicUsize, Ordering};
    static NEXT: AtomicUsize = AtomicUsize::new(0);
    struct Directory(std::path::PathBuf);
    impl Drop for Directory {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.0);
        }
    }
    let path = std::env::temp_dir().join(format!(
        "rea-save-test-{}-{}-{}",
        std::process::id(),
        NEXT.fetch_add(1, Ordering::Relaxed),
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos()
    ));
    fs::create_dir(&path).unwrap();
    let directory = Directory(path);
    let path = directory.0.join("preferences.json");
    assert_eq!(
        DemoPreferences::load(&path).unwrap(),
        DemoPreferences::default()
    );
    let expected = DemoPreferences {
        selected_menu: 1,
        display: rea_goku_hishoden::settings::DisplaySettings {
            scale: 6,
            palette: rea_goku_hishoden::settings::Palette::Blue,
        },
    };
    expected.store(&path).unwrap();
    assert_eq!(DemoPreferences::load(&path).unwrap(), expected);
    fs::write(&path, b"invalid json").unwrap();
    assert!(DemoPreferences::load(&path).is_err());
    assert_eq!(fs::read(&path).unwrap(), b"invalid json");
    fs::write(&path, vec![b' '; 4097]).unwrap();
    assert!(DemoPreferences::load(&path).is_err());
    fs::write(&path, br#"{"selected_menu":99}"#).unwrap();
    assert!(DemoPreferences::load(&path).is_err());
}

#[test]
fn fixed_labels_and_options_fit_the_logical_screen() {
    use rea_goku_hishoden::localization::layout;
    let catalog = Catalog::pt_br().unwrap();
    for key in [
        "demo.title",
        "menu.start",
        "menu.options",
        "menu.exit",
        "menu.controls",
        "demo.next",
        "common.back",
        "title.name",
        "title.subtitle",
        "title.demo",
        "title.start",
        "dialogue.reveal",
        "dialogue.finish",
        "dialogue.speaker",
    ] {
        assert!(
            catalog.text(key).chars().count() <= 18,
            "Texto excedente: {key}"
        );
    }
    for key in ["options.language", "options.controls"] {
        assert!(catalog.text(key).chars().count() <= 18);
    }
    for value in ["2", "6"] {
        assert!(
            catalog
                .text("options.scale")
                .replace("{value}", value)
                .chars()
                .count()
                <= 18
        );
    }
    for key in ["palette.green", "palette.blue", "palette.gray"] {
        assert!(
            catalog
                .text("options.palette")
                .replace("{value}", catalog.text(key))
                .chars()
                .count()
                <= 18
        );
    }
    let pages = layout::pages(catalog.text("demo.message"), 18, 6).unwrap();
    assert!(pages.len() > 1);
    assert!(pages.iter().all(|page| page.len() <= 6));
}

#[test]
fn options_change_scale_and_palette_without_leaving_the_screen() {
    use rea_goku_hishoden::scenes::{Action, App, Scene};
    use rea_goku_hishoden::settings::Palette;
    let mut app = App::default();
    app.handle(rea_goku_hishoden::scenes::Action::Start);
    app.handle(Action::Down);
    app.handle(Action::Confirm);
    assert_eq!(app.scene, Scene::Options);
    app.handle(Action::Right);
    assert_eq!(app.display.scale, 5);
    app.handle(Action::Right);
    app.handle(Action::Right);
    assert_eq!(app.display.scale, 2);
    app.handle(Action::Left);
    assert_eq!(app.display.scale, 6);
    app.handle(Action::Down);
    app.handle(Action::Confirm);
    assert_eq!(app.display.palette, Palette::Blue);
    app.handle(Action::Left);
    assert_eq!(app.display.palette, Palette::Green);
    app.handle(Action::Back);
    assert_eq!(app.scene, Scene::Menu);
    assert_eq!(app.display.scale, 6);
}

#[test]
fn old_preferences_gain_display_defaults_and_invalid_scales_are_rejected() {
    use rea_goku_hishoden::settings::DisplaySettings;
    let old: DemoPreferences = serde_json::from_str(r#"{"selected_menu":1}"#).unwrap();
    assert_eq!(old.display, DisplaySettings::default());
    for scale in [0, 1, 7, 255] {
        let value = DemoPreferences {
            display: DisplaySettings {
                scale,
                ..Default::default()
            },
            ..Default::default()
        };
        assert!(value.validate().is_err());
    }
}
