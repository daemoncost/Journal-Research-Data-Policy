from io import StringIO

from daemon_analysis_tools.function import print_string


def test_print_string(mocker):
    test_string = "Hello, World!"

    # Mock the sys.stdout to capture the output
    mock_stdout = mocker.patch("sys.stdout", new_callable=StringIO)

    print_string(test_string)

    # Assert that the printed output matches the expected string
    assert mock_stdout.getvalue().strip() == test_string
