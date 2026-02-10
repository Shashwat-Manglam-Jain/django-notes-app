"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { logout } from "@/lib/auth";
import { useAuthGuard } from "@/lib/useAuthGuard";
type User = {
  id: number;
  email: string;
};

type Note = {
  id: number;
  note_type: "personal" | "work";
  description: string;
  isActiveReq: boolean;
  validateDeleteManager: boolean;
  validateDeleteSuperAdmin: boolean;
};

export default function NotesPage() {useAuthGuard()
  const [role, setRole] = useState<"user" | "manager" | "superadmin">("user");
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);

  const [notes, setNotes] = useState<Note[]>([]);
  const [noteType, setNoteType] = useState<"personal" | "work">("personal");
  const [description, setDescription] = useState("");


useEffect(() => {
  const token = localStorage.getItem("access");

  if (!token) {
    setRole("user"); 
    return;
  }

  try {
    const payload = JSON.parse(atob(token.split(".")[1]));

    setRole(payload.role || "user");
  } catch (err) {
    console.error("Invalid token", err);
    setRole("user");
  }
}, []);



  useEffect(() => {
    if (role === "manager") {
      apiFetch("/user/").then(setUsers).catch(() => {});
    }
  }, [role]);


  const loadNotes = (userId?: number) => {
    const query = userId ? `?userId=${userId}` : "";
    apiFetch(`/notes/${query}`).then(setNotes).catch(logout);
  };

  useEffect(() => {
    loadNotes();
  }, []);


  const createNote = async () => {
    await apiFetch("/notes/", {
      method: "POST",
      body: JSON.stringify({ note_type: noteType, description }),
    });
    setDescription("");
    loadNotes();
  };

  const deleteNote = async (note: Note) => {
    if (note.note_type === "work" && role === "user") {
      alert(
        "You do not have permission to delete work notes directly. A delete request will be sent."
      );
    }

    await apiFetch(`/notes/${note.id}/`, { method: "DELETE" });
    loadNotes(selectedUserId ?? undefined);
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Notes Management</h1>
        <button className="btn w-auto px-4" onClick={logout}>
          Logout
        </button>
      </div>

      {role === "user" && (
        <div className="border p-4 rounded space-y-3">
          <h2 className="font-semibold">Create Note</h2>

          <select
            className="input"
            value={noteType}
            onChange={(e) => setNoteType(e.target.value as any)}
          >
            <option value="personal">Personal</option>
            <option value="work">Work</option>
          </select>

          <textarea
            className="input"
            placeholder="Write note..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />

          <button className="btn" onClick={createNote}>
            Create Note
          </button>
        </div>
      )}

      {role === "manager" && (
        <div>
          <h2 className="text-xl font-semibold mb-3">Users</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {users.map((u) => (
              <div
                key={u.id}
                onClick={() => {
                  setSelectedUserId(u.id);
                  loadNotes(u.id);
                }}
                className="cursor-pointer border rounded p-4 hover:bg-gray-50"
              >
                {u.email}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="space-y-3">
        {notes.map((note) => (
          <div
            key={note.id}
            className="border rounded p-4 flex justify-between"
          >
            <div>
              <p className="font-semibold capitalize">
                {note.note_type} note
              </p>
              <p className="text-sm">{note.description}</p>

              {note.isActiveReq && (
                <p className="text-xs text-orange-600">
                  ⚠ Delete request pending
                </p>
              )}
            </div>

            <button
              className="text-red-600 text-sm"
              onClick={() => deleteNote(note)}
            >
              Delete
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
