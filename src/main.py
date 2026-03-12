from typing import List, Union

import supervisely as sly
from supervisely.app.widgets import Button, Flexbox, ReorderTable

import src.globals as g

save_button = Button(text="Apply changes", icon="zmdi zmdi-save", button_size="small")
refresh_button = Button(text="Refresh", icon="zmdi zmdi-refresh", button_size="small")
buttons_flexbox = Flexbox(widgets=[save_button, refresh_button], gap=0)
save_button.disable()

reorder_table = ReorderTable(
    columns=g.COLUMNS, page_size=20, content_top_right=buttons_flexbox
)


def get_pointcloud_data() -> List[List[Union[int, str]]]:
    """Fetches the list of pointclouds for the current dataset in the correct frame order
    and returns their details as a list of lists.

    :return: A list of lists, where each inner list contains the details of a pointcloud (ID,
    name, figures count, objects count, created at, updated at).
    :rtype: List[List[Union[int, str]]]
    """
    pointcloud_infos = g.api.pointcloud_episode.get_list(g.DATASET_ID)
    frame_name_map = g.api.pointcloud_episode.get_frame_name_map(g.DATASET_ID)
    sly.logger.debug(
        f"Fetched {len(pointcloud_infos)} pointclouds for dataset {g.DATASET_ID}."
    )
    name_to_info = {info.name: info for info in pointcloud_infos}
    return [
        [
            name_to_info[name].id,
            name_to_info[name].name,
            name_to_info[name].figures_count,
            name_to_info[name].objects_count,
            name_to_info[name].created_at,
            name_to_info[name].updated_at,
        ]
        for _, name in sorted(frame_name_map.items())
    ]


def refresh_table_data() -> None:
    """Refreshes the data in the reorder table by fetching the latest pointcloud details and
    updating the table with the new data.
    """
    new_data = get_pointcloud_data()
    reorder_table.set_data(g.COLUMNS, new_data)


@reorder_table.order_changed
def on_order_changed(_: List[int]) -> None:
    """Event handler that is called when the order of frames in the reorder table is changed. It checks
    if the new order is different from the original order and enables or disables the save button
    accordingly.

    :param _: A list of integers representing the new order of frame IDs (not used in this function).
    :type _: List[int]
    """
    sly.logger.debug(
        "Order of frames has been changed. Checking if the save button should be enabled."
    )
    if reorder_table.is_order_changed():
        sly.logger.debug("Order of frames has been changed. Enabling the save button.")
        save_button.enable()
    else:
        sly.logger.debug(
            "Order of frames is the same as the original. Disabling the save button."
        )
        save_button.disable()


def update_button(succeed: bool) -> None:
    """Updates the save button's text, icon, and type based on whether the operation succeeded or failed.

    :param succeed: A boolean indicating whether the operation succeeded (True) or failed (False).
    :type succeed: bool
    """
    if succeed:
        save_button.text = "Changes applied"
        save_button.icon = "zmdi zmdi-check"
        save_button.button_type = "success"
    else:
        save_button.text = "Failed to apply changes"
        save_button.icon = "zmdi zmdi-close"
        save_button.button_type = "danger"


def reset_save_button() -> None:
    """Resets the save button to its default state (disabled, with original text and icon) after
    a refresh or when the order is changed back to the original.
    """
    save_button.text = "Apply changes"
    save_button.icon = "zmdi zmdi-save"
    save_button.button_type = "primary"
    save_button.disable()


@save_button.click
def update_order() -> None:
    """Saves the new order of frames by retrieving the updated list of frame IDs from the reorder
    table and sending it to the API. If the update is successful, the save button is updated to
    indicate success; if an error occurs, the button is updated to indicate failure and the error
    is logged and raised. Finally, the table data is refreshed to reflect any changes.
    """
    try:
        ids = reorder_table.get_column_data("ID")
        sly.logger.info(
            f"Saving new frame order for dataset {g.DATASET_ID}. Retrieved {len(ids)} frame IDs from the table."
        )
        g.api.pointcloud_episode.update_frames_order(g.DATASET_ID, ids)
        sly.logger.info(
            f"New frame order has been saved for dataset {g.DATASET_ID}. Refreshing table data."
        )
        update_button(succeed=True)
    except Exception as e:
        sly.logger.error(
            f"An error occurred while saving the new frame order for dataset {g.DATASET_ID}: {e}"
        )
        update_button(succeed=False)
        raise
    refresh_table_data()
    sly.logger.info(f"Saved new frame order for dataset {g.DATASET_ID}")


@refresh_button.click
def refresh_table() -> None:
    """Refreshes the table data by fetching the latest pointcloud details and resetting the save button."""
    reset_save_button()
    refresh_table_data()


refresh_table_data()
app = sly.Application(layout=reorder_table)
