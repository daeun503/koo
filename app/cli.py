import typer
from rich.console import Console

from app.enums import Domain, SourceType
from config import settings
from container.container import Container
from infra.vector_store.milvus.base import init_milvus

app = typer.Typer(
    add_completion=False,
    pretty_exceptions_enable=False,
)

ingest_app = typer.Typer(
    pretty_exceptions_enable=False,
)

app.add_typer(ingest_app, name="ingest")


@app.callback()
def _init(ctx: typer.Context):
    init_milvus(
        host=settings.MILVUS_HOST,
        port=settings.MILVUS_PORT,
        dim=settings.EMBEDDING_DIM,
    )

    ctx.obj = {"container": Container(), "console": Console()}


@app.command("ask")
def ask_cmd(
    context: typer.Context,
    query: str = typer.Argument(...),
):
    container = context.obj["container"]
    console = context.obj["console"]

    ask_service = container.ask_service()

    answer = ask_service.ask(query)
    ask_service.print_answer(console=console, answer=answer)


@ingest_app.command("text")
def ingest_raw_text(
    context: typer.Context,
    domain: Domain = typer.Option(Domain.CS),
    source_id: str = typer.Option(...),
    title: str | None = typer.Option(None),
    content: str = typer.Option(...),
):
    container = context.obj["container"]
    console = context.obj["console"]

    pipeline = container.ingest_service()
    ingestor = container.ingestor_factory().create(
        domain=domain,
        source_type=SourceType.RAW_TEXT,
        source_id=source_id,
        title=title,
        content=content,
    )
    result = pipeline.ingest(ingestor=ingestor)
    console.print(f"[green]OK[/green] document_id={result['document_id']} chunks={result['chunks']}")


@ingest_app.command("notion")
def ingest_notion(
    context: typer.Context,
    domain: Domain = typer.Option(Domain.CS),
    source_id: str = typer.Option(...),
):
    container = context.obj["container"]
    console = context.obj["console"]

    pipeline = container.ingest_service()
    ingestor = container.ingestor_factory().create(
        domain=domain,
        source_type=SourceType.NOTION,
        source_id=source_id,
    )
    result = pipeline.ingest(ingestor=ingestor)
    console.print(f"[green]OK[/green] document_id={result['document_id']} chunks={result['chunks']}")


@ingest_app.command("file")
def ingest_file(
    context: typer.Context,
    domain: Domain = typer.Option(Domain.CS),
    source_id: str = typer.Option(...),
):
    container = context.obj["container"]
    console = context.obj["console"]

    pipeline = container.ingest_service()
    ingestor = container.ingestor_factory().create(
        domain=domain,
        source_type=SourceType.FILE,
        source_id=source_id,
    )
    result = pipeline.ingest(ingestor=ingestor)
    console.print(f"[green]OK[/green] document_id={result['document_id']} chunks={result['chunks']}")
