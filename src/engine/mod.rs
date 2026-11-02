use crate::assets;
use crate::localization::Catalog;
use crate::save::DemoPreferences;
use crate::scenes::dialogue::Dialogue;
use crate::scenes::{Action, App, Scene};
use sdl3::event::Event;
use sdl3::keyboard::{Keycode, Mod};
use sdl3::pixels::Color;
use sdl3::rect::Rect;
use sdl3::render::{create_renderer, Canvas};
use sdl3::video::Window;
use std::path::Path;
use std::time::{Duration, Instant};

pub const WIDTH: u32 = 160;
pub const HEIGHT: u32 = 144;
const COLUMNS: usize = 18;
const CONTENT_ROWS: usize = 6;

fn text(
    canvas: &mut Canvas<Window>,
    value: &str,
    x: i32,
    y: i32,
    scale: u32,
) -> Result<(), String> {
    for (column, character) in value.chars().enumerate() {
        let glyph =
            assets::glyph(character).ok_or_else(|| format!("Glifo ausente: {character}"))?;
        for (gy, bits) in glyph.iter().enumerate() {
            for gx in 0..8 {
                if bits & (1 << gx) != 0 {
                    let logical_x = x + column as i32 * 8 + gx;
                    let logical_y = y + gy as i32;
                    if logical_x < 0
                        || logical_y < 0
                        || logical_x >= WIDTH as i32
                        || logical_y >= HEIGHT as i32
                    {
                        continue;
                    }
                    canvas
                        .fill_rect(Rect::new(
                            logical_x * scale as i32,
                            logical_y * scale as i32,
                            scale,
                            scale,
                        ))
                        .map_err(|error| error.to_string())?;
                }
            }
        }
    }
    Ok(())
}

pub fn run() -> Result<(), String> {
    run_inner(false)
}

/// Exercita somente recursos próprios; não lê nem grava preferências.
pub fn smoke_test() -> Result<(), String> {
    run_inner(true)
}

fn smoke_key(frame: u32) -> Option<Keycode> {
    match frame {
        1 => Some(Keycode::Return),
        2 | 3 | 4 | 8 | 17 | 36 => Some(Keycode::Z),
        5 => Some(Keycode::Left),
        6 | 15 | 37 => Some(Keycode::Escape),
        7 | 12 => Some(Keycode::Down),
        9 | 10 | 11 | 13 | 14 => Some(Keycode::Right),
        16 => Some(Keycode::Up),
        _ => None,
    }
}

fn run_inner(smoke: bool) -> Result<(), String> {
    let catalog = Catalog::pt_br()?;
    let dialogue = Dialogue::new(catalog.text("demo.message"), COLUMNS, CONTENT_ROWS)?;
    let mut app = App::new(dialogue);
    let save_path = Path::new("saves/demo-preferences.json");
    let can_save = if smoke {
        false
    } else {
        match DemoPreferences::load(save_path) {
            Ok(preferences) => {
                app.menu.restore(preferences.selected_menu)?;
                app.display = preferences.display;
                true
            }
            Err(error) => {
                // Preserva o arquivo inválido para diagnóstico, sem substituí-lo ao sair.
                eprintln!("Preferências não carregadas: {error}");
                false
            }
        }
    };
    let initial_scale = u32::from(app.display.scale);
    let context = sdl3::init().map_err(|error| format!("Inicialização da SDL3: {error}"))?;
    let video = context
        .video()
        .map_err(|error| format!("Acesso ao vídeo: {error}"))?;
    // Janela fixa: coordenadas lógicas multiplicadas por inteiro, sem filtragem.
    let window = video
        .window(
            "REA — demonstração",
            WIDTH * initial_scale,
            HEIGHT * initial_scale,
        )
        .position_centered()
        .build()
        .map_err(|error| format!("Criação da janela: {error}"))?;
    let mut canvas = create_renderer(window, None)
        .map_err(|error| format!("Criação do renderizador: {error}"))?;
    let mut events = context.event_pump().map_err(|error| error.to_string())?;
    let mut smoke_frame = 0;
    let mut visited = [false; 4];
    let mut last_tick = Instant::now();
    'running: loop {
        let now = Instant::now();
        app.tick(if smoke {
            Duration::from_millis(16)
        } else {
            now.duration_since(last_tick)
                .min(Duration::from_millis(250))
        });
        last_tick = now;
        let scripted_event = if smoke {
            smoke_key(smoke_frame).map(|key| Event::KeyDown {
                timestamp: 0,
                window_id: canvas.window().id(),
                keycode: Some(key),
                scancode: None,
                keymod: Mod::NOMOD,
                repeat: false,
                which: 0,
                raw: 0,
            })
        } else {
            None
        };
        for event in events.poll_iter().chain(scripted_event) {
            let action = match event {
                Event::Quit { .. } => break 'running,
                Event::KeyDown {
                    keycode: Some(key),
                    repeat: false,
                    ..
                } => match key {
                    Keycode::Escape => Some(Action::Back),
                    Keycode::Up => Some(Action::Up),
                    Keycode::Down => Some(Action::Down),
                    Keycode::Return => Some(Action::Start),
                    Keycode::Z => Some(Action::Confirm),
                    Keycode::Right => Some(Action::Right),
                    Keycode::Left => Some(Action::Left),
                    _ => None,
                },
                _ => None,
            };
            if let Some(action) = action {
                if !app.handle(action) {
                    break 'running;
                }
            }
        }
        let scale = u32::from(app.display.scale);
        let size = (WIDTH * scale, HEIGHT * scale);
        if canvas.window().size() != size {
            canvas
                .window_mut()
                .set_size(size.0, size.1)
                .map_err(|error| format!("Ajuste da janela: {error}"))?;
        }
        let (background, foreground) = app.display.palette.colors();
        canvas.set_draw_color(Color::RGB(background[0], background[1], background[2]));
        canvas.clear();
        canvas.set_draw_color(Color::RGB(foreground[0], foreground[1], foreground[2]));
        if app.scene != Scene::Title {
            text(&mut canvas, catalog.text("demo.title"), 8, 12, scale)?;
        }
        match app.scene {
            Scene::Title => {
                canvas
                    .draw_rect(Rect::new(
                        8 * scale as i32,
                        16 * scale as i32,
                        144 * scale,
                        110 * scale,
                    ))
                    .map_err(|error| error.to_string())?;
                text(&mut canvas, catalog.text("title.name"), 24, 32, scale)?;
                text(&mut canvas, catalog.text("title.subtitle"), 24, 52, scale)?;
                text(&mut canvas, catalog.text("title.demo"), 24, 72, scale)?;
                text(&mut canvas, catalog.text("title.start"), 24, 100, scale)?;
            }
            Scene::Menu => {
                for (index, key) in ["menu.start", "menu.options", "menu.exit"]
                    .iter()
                    .enumerate()
                {
                    let y = 44 + index as i32 * 20;
                    if index == app.menu.selected() {
                        text(&mut canvas, ">", 0, y, scale)?;
                    }
                    text(&mut canvas, catalog.text(key), 8, y, scale)?;
                }
                text(&mut canvas, catalog.text("menu.controls"), 8, 112, scale)?;
            }
            Scene::Example => {
                text(&mut canvas, catalog.text("dialogue.speaker"), 8, 26, scale)?;
                canvas
                    .draw_rect(Rect::new(
                        4 * scale as i32,
                        36 * scale as i32,
                        152 * scale,
                        70 * scale,
                    ))
                    .map_err(|error| error.to_string())?;
                for (row, line) in app.dialogue.visible_lines().iter().enumerate() {
                    text(&mut canvas, line, 8, 40 + row as i32 * 10, scale)?;
                }
                let counter = format!(
                    "{}/{}",
                    app.dialogue.page_index() + 1,
                    app.dialogue.page_count()
                );
                text(&mut canvas, &counter, 120, 26, scale)?;
                let hint = if !app.dialogue.fully_revealed() {
                    "dialogue.reveal"
                } else if app.dialogue.is_last_page() {
                    "dialogue.finish"
                } else {
                    "demo.next"
                };
                text(&mut canvas, catalog.text(hint), 8, 112, scale)?;
            }
            Scene::Options => {
                text(&mut canvas, catalog.text("options.language"), 8, 36, scale)?;
                let scale_label = catalog
                    .text("options.scale")
                    .replace("{value}", &scale.to_string());
                let palette_label = catalog.text("options.palette").replace(
                    "{value}",
                    catalog.text(app.display.palette.localization_key()),
                );
                for (index, label) in [scale_label, palette_label].iter().enumerate() {
                    let y = 56 + index as i32 * 18;
                    if index == app.option {
                        text(&mut canvas, ">", 0, y, scale)?;
                    }
                    text(&mut canvas, label, 8, y, scale)?;
                }
                text(&mut canvas, catalog.text("options.controls"), 8, 104, scale)?;
            }
        }
        text(&mut canvas, catalog.text("common.back"), 8, 128, scale)?;
        canvas.present();
        if smoke {
            visited[match app.scene {
                Scene::Title => 0,
                Scene::Menu => 1,
                Scene::Example => 2,
                Scene::Options => 3,
            }] = true;
            if smoke_frame == 35
                && (app.dialogue.fully_revealed()
                    || app.dialogue.visible_lines().iter().all(String::is_empty))
            {
                return Err("Texto progressivo não percorreu o estado parcial".into());
            }
            smoke_frame += 1;
            if smoke_frame == 38 {
                if visited.iter().any(|seen| !seen)
                    || app.scene != Scene::Menu
                    || app.display.scale != 2
                    || app.display.palette != crate::settings::Palette::Gray
                    || canvas.output_size().map_err(|error| error.to_string())? != (320, 288)
                {
                    return Err("Percurso SDL não corresponde ao esperado".into());
                }
                break 'running;
            }
        } else {
            std::thread::sleep(Duration::from_millis(16));
        }
    }
    if smoke && smoke_frame != 38 {
        return Err("Percurso SDL interrompido antes de concluir".into());
    }
    if can_save {
        DemoPreferences {
            selected_menu: app.menu.selected(),
            display: app.display,
        }
        .store(save_path)?;
    }
    Ok(())
}
