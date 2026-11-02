fn main() -> Result<(), String> {
    let args: Vec<String> = std::env::args().skip(1).collect();
    match args.as_slice() {
        [] => rea_goku_hishoden::engine::run(),
        [flag] if flag == "--smoke-test" => rea_goku_hishoden::engine::smoke_test(),
        _ => Err("Uso: rea-goku-hishoden [--smoke-test]".into()),
    }
}
