import typer
from rich.console import Console
from rich.table import Table

from app.container import Container
from app.enums import Domain, RouterDomain, SourceType
from app.ingest.source_ingestor import IngestorFactory
from config import settings
from infra.vector_store.milvus.base import init_milvus

app = typer.Typer(add_completion=False)
console = Console()

ingest_app = typer.Typer()
app.add_typer(ingest_app, name="ingest")


@app.callback()
def _init(ctx: typer.Context):
    init_milvus(
        host=settings.MILVUS_HOST,
        port=settings.MILVUS_PORT,
        dim=settings.EMBEDDING_DIM,
    )

    ctx.obj = {"container": Container(), "console": console}


@ingest_app.command("text")
def ingest_text_cmd(
    context: typer.Context,
    domain: Domain = typer.Option(...),
    source_type: SourceType = typer.Option(...),
    source_id: str = typer.Option(...),
    title: str | None = typer.Option(None),
    content: str | None = typer.Option(None),
):
    container = context.obj["container"]
    console = context.obj["console"]

    pipeline = container.ingest_pipeline()

    ingestor = IngestorFactory.create(
        domain=domain,
        source_type=source_type,
        source_id=source_id,
        title=title,
        content=content,
    )
    result = pipeline.ingest(ingestor=ingestor)

    console.print(f"[green]OK[/green] document_id={result['document_id']} chunks={result['chunks']}")


@app.command("ask")
def ask_cmd(
    context: typer.Context,
    query: str = typer.Argument(...),
    domain: RouterDomain | None = typer.Option(None),
    topk: int = 3,
):
    container = context.obj["container"]

    answerer = container.answerer()
    retriever = container.retriever()

    routed = domain or retriever.route_to_domain(query)
    hits = retriever.get_hits(routed, query)

    table = Table(title=f"koo retrieve (route={routed}, topk={topk})")
    table.add_column("rank", justify="right")
    table.add_column("chunk_id", justify="right")
    table.add_column("score", justify="right")
    table.add_column("preview")

    selected_ids = []
    for i, h in enumerate(hits, start=1):
        selected_ids.append(int(h["chunk_id"]))
        preview = (h["chunk_text"] or "").replace("\n", " ")
        if len(preview) > 120:
            preview = preview[:120] + "..."
        table.add_row(str(i), str(h["chunk_id"]), f"{h['score']:.4f}", preview)
    console.print(table)

    answer = answerer.answer(query, hits)
    # MySQLQueryLogWrapper.create(
    #     query_text=query,
    #     router_domain=routed,
    #     topk=topk,
    #     selected_chunk_ids=selected_ids,
    #     answer=answer,
    # )

    console.print("\n[bold]Answer[/bold]")
    console.print(answer)
