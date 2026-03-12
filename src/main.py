import supervisely as sly
import src.globals as g
from supervisely.app.widgets import Container

from supervisely.app.widgets import ReorderTable, Button, Text

columns = [
    "ID",
    "Name",
    "Figures count",
    "Objects count",
    "Created At",
    "Updated At",
]

reorder_table = ReorderTable(columns=columns)
update_button = Button(
    text="Apply changes", button_type="primary", icon="zmdi zmdi-save"
)
update_text = Text(text="", status="info")
update_button.disable()

pointcloud_infos = g.api.pointcloud.get_list(g.DATASET_ID)

data = [
    [
        pointcloud_info.id,
        pointcloud_info.name,
        pointcloud_info.figures_count,
        pointcloud_info.objects_count,
        pointcloud_info.created_at,
        pointcloud_info.updated_at,
    ]
    for pointcloud_info in pointcloud_infos
]
reorder_table.set_data(columns, data)


@reorder_table.order_changed
def on_order_changed(_order) -> None:
    update_text.text = ""
    update_text.hide()
    if reorder_table.is_order_changed():
        update_button.enable()
    else:
        update_button.disable()


@update_button.click
def update_order() -> None:
    ids = reorder_table.get_column_data("ID")
    g.api.pointcloud_episode.update_frames_order(g.DATASET_ID, ids)
    reordered_data = reorder_table.get_reordered_data()
    reorder_table.set_data(columns, reordered_data)
    sly.logger.info(f"Saved new frame order for dataset {g.DATASET_ID}")

    update_text.text = "The order of frames has been updated successfully."
    update_text.status = "success"
    update_text.show()


layout = Container(widgets=[reorder_table, update_button, update_text])

app = sly.Application(layout=layout)
