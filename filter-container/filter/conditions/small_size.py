import logging
import os

from .utils import validate_inputs_outputs, get_size_of_dir

l = logging.getLogger("[small_size]")

DEFAULT_SMALLER_THAN_PCT = 0.1


class SmallSize:
    """Checks if the outputs size complies with our size conditions.
    The default condition, that can be overwritten by setting SMALLER_THAN_PCT
    env variable, is that all the files in the folder that is defined
    by the OUTPUTS env variable should be lass than SMALLER_THAN_PCT * INPUTS.
    Where INPUTS is the folder containing all the inputs defined by that env
    variable. So:

    OUTPUTS <= SMALLER_THAN_PCT * INPUTS

    has to hold. Note that the range of values of SMALLER_THAN_PCT is: [0, 1].
    i.e. it can be 0.1, which would mean 10%. 0.45, would mean 45% and so on.
    Note that setting it to 0 would mean this small size condition would never
    be satisfied. Likewise, setting it to 1, would mean that it is always
    satisfied.
    """

    def __init__(self):
        self.name = "SmallSize"
        self.inputs = os.getenv("INPUTS", "")
        self.outputs = os.getenv("OUTPUTS", "")
        self.size_threshold = DEFAULT_SMALLER_THAN_PCT

    def __call__(self) -> bool:
        """Call class's instance to get back a bool that indicates if the size of
        the output complies with our thresholds. Returns True if it does, else False.
        Note that this class traverses **ALL** files stored in the path defined by
        env variable INPUTS and also OUTPUTS (separately). It then compares that
        OUPUTS <= SMALLER_THAN_PCT * OUTPUTS. SMALLER_THAN_PCT default is 0.1 (i.e. 10%).
        You may need to change the logic of traversing all the files if we suddenly store
        some meta data or other unrelated data in either of those folders.

        Returns:
            bool: Signals if the outputs files are <= SMALLET_THAN_PCT * inputs_files_sizes
        """
        is_valid = self._validate_envs()
        if not is_valid:
            return False

        total_inputs_size = get_size_of_dir(self.inputs)

        if total_inputs_size < 1:
            l.error(f"size of all of the input files in {self.inputs} is zero")
            return False

        total_outputs_size = get_size_of_dir(self.outputs)

        if not total_outputs_size <= self.size_threshold * total_inputs_size:
            l.error(
                f"outputs size is too large. {total_outputs_size=} bytes"
                f", {total_inputs_size=} bytes, {self.size_threshold=}"
            )
            return False

        return True

    def _validate_envs(self) -> bool:
        """This function validates that all of the environment variables that we need
        are defined. If they all are, we assign them to instance's attributes.

        Returns:
            bool: True if it they are validated. Then we have succesffully assigned
            them as instance's attributes. Else, we log the error and we stop immediately.
        """
        size_threshold = float(os.getenv("SMALLER_THAN_PCT", self.size_threshold))

        if size_threshold < 0.0 or size_threshold > 1.0:
            l.error(
                "invalid size_threshold units. This should in pct, i.e. the range that this can take is [0, 1]. For example, 0.1 for 10%, 0.2 for 20%"
            )
            return False

        self.size_threshold = size_threshold

        is_valid = validate_inputs_outputs()

        if not is_valid:
            return False

        # ! do not remove from here, since in tests we define them after we instantiate
        # ! alternatively, define them before we instantiate. in any case, no harm here
        self.inputs = os.getenv("INPUTS", "")
        self.outputs = os.getenv("OUTPUTS", "")

        return True
