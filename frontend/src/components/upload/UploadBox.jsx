import { useRef } from "react";
import { FaCloudUploadAlt } from "react-icons/fa";

function UploadBox({ file, setFile }) {
    const inputRef = useRef(null);

    const handleFile = (selectedFile) => {
        if (!selectedFile) return;

        if (!selectedFile.name.toLowerCase().endsWith(".xml")) {
            alert("Only XML files are supported.");
            return;
        }

        setFile(selectedFile);
    };

    const onDrop = (e) => {
        e.preventDefault();
        handleFile(e.dataTransfer.files[0]);
    };

    return (
        <div
            onClick={() => inputRef.current.click()}
            onDragOver={(e) => e.preventDefault()}
            onDrop={onDrop}
            className="border-2 border-dashed border-green-500 rounded-xl p-12 cursor-pointer hover:bg-slate-800 transition"
        >
            <input
                ref={inputRef}
                type="file"
                hidden
                accept=".xml"
                onChange={(e) => handleFile(e.target.files[0])}
            />

            <div className="flex flex-col items-center gap-4">

                <FaCloudUploadAlt
                    className="text-6xl text-green-400"
                />

                <h2 className="text-2xl font-bold">
                    Drag & Drop XML Scan
                </h2>

                <p className="text-slate-400">
                    or click here to browse
                </p>

                {file && (
                    <div className="mt-4 bg-slate-900 px-5 py-3 rounded-lg border border-green-500">
                        {file.name}
                    </div>
                )}

            </div>
        </div>
    );
}

export default UploadBox;