import pandas as pd

def extract_data(request):
    acc_x = request.json["xVals"]
    acc_y = request.json["yVals"]
    acc_z = request.json["zVals"]
    test_name = request.json["testName"]

    t_vals = request.json["timeVals"]

    df = pd.DataFrame({"x": acc_x, "y": acc_y, "z": acc_z, "T": t_vals})

    df.to_csv(f"/home/cwall96/csvs/{test_name}.csv")

    return df, acc_x, acc_y, acc_z