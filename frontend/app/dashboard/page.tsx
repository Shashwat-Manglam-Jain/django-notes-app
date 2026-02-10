"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { logout } from "@/lib/auth";
import { useAuthGuard } from "@/lib/useAuthGuard";


type User = {
  id: number;
  email: string;
};

type Note = {
  id: number;
  description: string;
  note_type: "personal" | "work";
  isActiveReq: boolean;
  validateDeleteManager: boolean;
  validateDeleteSuperAdmin: boolean;
};

type Me = {
  id: number;
  email: string;
  role: "user" | "manager" | "superadmin";
};

export default function Dashboard() {
  useAuthGuard(); 

  const router = useRouter();

  const [me, setMe] = useState<Me | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);

  useEffect(() => {
    apiFetch("/me/")
      .then(setMe)
      .catch(logout);
  }, []);

  useEffect(() => {
    if (me && me.role === "manager") {
      apiFetch("/user/")
        .then(setUsers)
        .catch(() => {});
    }
  }, [me]);

  const loadNotes = (userId?: number) => {
    const query = userId ? `?userId=${userId}` : "";
    apiFetch(`/notes/${query}`)
      .then(setNotes)
      .catch(logout);
  };

  useEffect(() => {
    if (me && me.role === "user") {
      loadNotes();
    }
  }, [me]);

const deleteNote = async (note: Note) => {
  setNotes((prev) => prev.filter((n) => n.id !== note.id));

  if (note.note_type === "work" && me?.role === "user") {
    alert("Delete request sent to manager");
  }

  try {
    await apiFetch(`/notes/${note.id}/`, { method: "DELETE" });
  } catch {
   
    loadNotes(selectedUserId ?? undefined);
  }
};

 
const approveDelete = async (noteId: number) => {
  
  setNotes((prev) => prev.filter((n) => n.id !== noteId));

  try {
    await apiFetch(`/notes/${noteId}/`, { method: "DELETE" });
  } catch {
    loadNotes(selectedUserId ?? undefined);
  }
};


  if (!me) return null;

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">

      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <button className="btn px-4" onClick={logout}>
          Logout
        </button>
      </div>

      <div className="border rounded p-4 bg-gray-50">
        <p className="font-medium text-black-400">
          Welcome, <span className="text-blue-600">{me.email}</span>
        </p>
        <p className="text-sm text-gray-600">Role: {me.role}</p>
      </div>

      {me.role === "manager" && users.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold mb-3">Users</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {users.map((u) => (
              <div
                key={u.id}
                onClick={() => {
                  setSelectedUserId(u.id);
                  loadNotes(u.id);
                }}
                className={`cursor-pointer border rounded p-4 transition
                  ${
                    selectedUserId === u.id
                      ? "border-black bg-gray-100"
                      : "hover:bg-gray-50"
                  }`}
              >
                <p className="font-medium">{u.email}</p>
                <p className="text-xs text-gray-500">
                  Click to view work notes
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

    
      <div>
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-xl font-semibold">
            {me.role === "user" ? "My Notes" : "Work Notes"}
          </h2>

          <button
            className="text-sm text-blue-600 hover:underline"
            onClick={() =>
              router.push(
                selectedUserId
                  ? `/notes?userId=${selectedUserId}`
                  : "/notes"
              )
            }
          >
            Open full notes →
          </button>
        </div>

        {notes.length === 0 ? (
          <p className="text-sm text-gray-500">No notes available</p>
        ) : (
          <div className="space-y-3">
            {notes.map((note) => (
              <div
                key={note.id}
                className="border rounded p-4 flex justify-between items-start"
              >
                <div>
                  <p className="text-sm">{note.description}</p>

                  {note.isActiveReq && (
                    <p className="text-xs text-orange-600 mt-1">
                      ⚠ Delete request pending
                    </p>
                  )}
                </div>

               
                {me.role === "user" && (
                  <button
                    className="text-red-600 text-sm"
                    onClick={() => deleteNote(note)}
                  >
                    Delete
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      
      {me.role === "manager" && (
        <div className="border rounded p-4 bg-red-50">
          <h2 className="text-lg font-semibold mb-3 text-red-700">
            Pending Delete Requests
          </h2>

          {notes.filter((n) => n.isActiveReq).length === 0 ? (
            <p className="text-sm text-gray-500">
              No pending delete requests
            </p>
          ) : (
            <div className="space-y-3">
              {notes
                .filter((n) => n.isActiveReq)
                .map((n) => (
                  <div
                    key={n.id}
                    className="border rounded p-4 flex justify-between items-center bg-white"
                  >
                    <p className="text-sm">{n.description}</p>
                    <button
                      className="btn bg-red-600 text-white"
                      onClick={() => approveDelete(n.id)}
                    >
                      Approve Delete
                    </button>
                  </div>
                ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
